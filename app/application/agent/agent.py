
from pathlib import Path
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from app.domain.agent_state import AgentState
from app.infraestructure.file_utils.utils import save_code, linter_ruff, snapshot_state, agent_history, clean_output

class Agent:
    def __init__(self, llm, prompt_path):
        self.llm = llm
        self.prompt_path = prompt_path
        
        # Construir el grafo de estados usando langgraph
        graph = StateGraph(AgentState)
        graph.add_node("security", self.security)
        graph.add_node("generator1", self.generator1)
        graph.add_node("generator2", self.generator2)
        graph.add_node("generator3", self.generator3)
        graph.add_node("aggregator", self.aggregator)
        graph.add_node("validator", self.validator)
        graph.add_node("saver", self.save)
        graph.add_node("linter", self.linter)
        graph.add_node("finisher", self.finisher)
       
        # Flujo:
        graph.add_conditional_edges(
            "security",
            self.sec_done,
            {True: "finisher", False: "generator1"}
        )
        graph.add_edge("generator1", "generator2")
        graph.add_edge("generator2", "generator3")
        graph.add_edge("generator3", "aggregator")
        graph.add_edge("aggregator", "validator")
        graph.add_conditional_edges(
            "validator",
            self.check_done,
            {True: "saver", False: "aggregator"}
        )
        graph.add_edge("saver", "linter")
        graph.add_conditional_edges(
            "linter",
            self.check_done,
            {True: "finisher", False: "aggregator"}
        )
        graph.add_edge("finisher", END)
        
        graph.set_entry_point("security")
        self.graph = graph.compile()

    def generator1(self, state: AgentState) -> AgentState:
        return self._generator(state, slot="generated_code_1")
    def generator2(self, state: AgentState) -> AgentState:
        return self._generator(state, slot="generated_code_2")
    def generator3(self, state: AgentState) -> AgentState:
        return self._generator(state, slot="generated_code_3")

    def _generator(self, state: AgentState, slot: str) -> AgentState:
        """Genera un nuevo código"""

        promt_select = {
            "generated_code_1":"user_generator1.txt",
            "generated_code_2":"user_generator2.txt",
            "generated_code_3":"user_generator3.txt"
        }

        prompt_input = Path(f'{self.prompt_path}/{promt_select[slot]}').read_text()
        prompt_system = Path(f'{self.prompt_path}/sys_generator.txt').read_text()

        prompt_input = prompt_input.format(
            descripcion = state.descripcion
        )
        new_code = self.llm.chat(prompt=prompt_input,sys_promt=prompt_system,temperature=0.2)

        setattr(state, slot, new_code)
        state.history.append({f"NODE_{slot.upper()}_it{state.n_iterations}": snapshot_state(state)})
        return state
    
    def aggregator(self, state: AgentState) -> AgentState:
        """Toma los 3 casos generados y genera un último caso"""
        print('-'*30,'>')
        print(f"SATE AGREGATOR IT {state.n_iterations}:\n{state}")
        prompt_aggregator = Path(f'{self.prompt_path}/user_aggregator.txt').read_text()
        prompt_system = Path(f'{self.prompt_path}/sys_generator.txt').read_text()
        if state.feedback.strip().upper() not in ["OK",""]:
            feedback_prompt = f"### Feedback\n{state.feedback.strip()}\n\n* Este es el código sobre el que se ha realizado el feedback::\n{state.generated_code}"
        else:
            feedback_prompt = ""
        prompt_aggregator = prompt_aggregator.format(
            descripcion_usuario = state.descripcion,
            codigo_1 = state.generated_code_1,
            codigo_2 = state.generated_code_2,
            codigo_3 = state.generated_code_3,
            feedback = feedback_prompt
        )
        new_code = self.llm.chat(prompt=prompt_aggregator,sys_promt=prompt_system)
        state.generated_code = new_code
        print(f"SATE AGREGATOR IT {state.n_iterations}:\n{state}")
        print('<','-'*30)
        state.history.append({f"NODE_AGGREGATOR_it{state.n_iterations}":snapshot_state(state)})
        return state

    def validator(self, state: AgentState) -> AgentState:
        """Valida el código generado y emite un juicio que se usa para decidir si se finaliza o no el proceso"""
        prompt_validator = Path(f'{self.prompt_path}/user_validator.txt').read_text()
        prompt_system = Path(f'{self.prompt_path}/sys_generator.txt').read_text()

        prompt_validator = prompt_validator.format(
            descripcion_usuario = state.descripcion,
            codigo_generado = state.generated_code
        )

        feedback = self.llm.chat(prompt=prompt_validator,sys_promt=prompt_system)
        state.feedback = feedback

        # Aquí se define el estado del flujo
        state.process_done = (feedback.upper() == "OK") or state.n_iterations>10
        print('-'*30,'>')
        print(f"VALIDATOR:\n{state}")
        print('<','-'*30)
        state.history.append({f"NODE_VALIDATOR_it{state.n_iterations}":snapshot_state(state)})
        if not state.process_done:
            state.n_iterations += 1
        return state

    def save(self, state: AgentState) -> None:
        """Guarda el código generado"""
        print('-'*30,'>')
        print(f"SAVER:\n{state}")
        print('<','-'*30)

        save_code(state.generated_code)

    def linter(self, state:AgentState) -> AgentState:
        """Nodo de validación con el liter ruff"""
        code, stdout = linter_ruff()
        if code==0:
            state.feedback = "OK"
            state.process_done = (state.feedback.upper() == "OK") or state.n_iterations>10
            state.history.append({f"NODE_LINTER_it{state.n_iterations}":snapshot_state(state)})
            return state
        state.feedback = f"A continuación, los problemas detectados por el linter Ruff: {stdout}"
        state.process_done = state.n_iterations>50
        state.history.append({f"NODE_LINTER_it{state.n_iterations}":snapshot_state(state)})
        if not state.process_done:
            state.n_iterations += 1
        return state

    def security(self, state: AgentState) -> AgentState:
        """Nodo de seguridad que detecta si el prompt del usuario es peligroso o no"""
        prompt_security = Path(f'{self.prompt_path}/sec_layer.txt').read_text()

        prompt_security = prompt_security.format(
            descripcion = state.descripcion
        )

        feedback = self.llm.chat(prompt=prompt_security,sys_promt=None)
        state.feedback = f"Prompt {feedback}"

        state.process_done = (feedback.lower() != "seguro")

        if state.process_done:
            clean_output()

        state.history.append({f"NODE_SECURITY_it{state.n_iterations}":snapshot_state(state)})

        return state        

    def sec_done(self, state: AgentState) -> bool:
        """Nodo de decisión que confirma si continua el flujo o el mensaje es peligroso y hay que finalizarlo"""
        return state.process_done

    def check_done(self, state: AgentState) -> bool:
        return state.process_done
    
    def finisher(self, state: AgentState) -> None:
        agent_history(state.history)
    
    def run(self, descripcion: str) -> AgentState:
        state = AgentState(descripcion= descripcion)
        final_state = self.graph.invoke(state, {"recursion_limit": 100})
        return final_state