# {"Depends": "py-genlayer:test"}

from genlayer import *
import json

@allow_storage
@dataclass
class Project:
    project_id: str
    owner: str
    name: str
    description: str
    stack: str
    status: str
    created_at: str
    updated_at: str
    active_skill_ids: str
    active_plugin_ids: str
    goal_ids: str
    contributor_addresses: str
    is_public: bool
    snapshot_count: u256

@allow_storage
@dataclass
class CodeFile:
    path: str
    language: str
    content: str
    explanation: str
    version: u256
    created_at: str
    updated_at: str
    created_by: str
    tags: str

@allow_storage
@dataclass
class FileVersion:
    version: u256
    content: str
    diff_summary: str
    timestamp: str
    author: str

@allow_storage
@dataclass
class Task:
    task_id: str
    project_id: str
    goal_id: str
    title: str
    description: str
    assigned_agent: str
    status: str
    priority: str
    depends_on: str
    output_files: str
    error_log: str
    retry_count: u256
    created_at: str
    completed_at: str

@allow_storage
@dataclass
class Goal:
    goal_id: str
    project_id: str
    description: str
    acceptance_criteria: str
    task_ids: str
    status: str
    created_at: str

@allow_storage
@dataclass
class MemoryEntry:
    entry_id: str
    project_id: str
    content: str
    category: str
    timestamp: str

@allow_storage
@dataclass
class Instruction:
    preset_name: str
    system_prompt: str
    temperature_hint: str
    output_format: str
    created_by: str
    created_at: str

@allow_storage
@dataclass
class AuditEntry:
    action: str
    actor: str
    project_id: str
    detail: str
    timestamp: str

@allow_storage
@dataclass
class SkillConfig:
    skill_name: str
    description: str
    prompt_fragment: str
    version: str
    is_builtin: bool

@allow_storage
@dataclass
class PluginConfig:
    plugin_name: str
    description: str
    trigger: str
    instruction: str

class SiggyCoder(gl.Contract):
    owner: Address
    version: str
    is_paused: bool
    projects: TreeMap[str, Project]
    project_index: DynArray[str]
    user_projects: TreeMap[str, DynArray[str]]
    project_files: TreeMap[str, TreeMap[str, CodeFile]]
    file_versions: TreeMap[str, DynArray[FileVersion]]
    tasks: TreeMap[str, Task]
    project_tasks: TreeMap[str, DynArray[str]]
    goals: TreeMap[str, Goal]
    project_goals: TreeMap[str, DynArray[str]]
    active_skills: TreeMap[str, DynArray[str]]
    active_plugins: TreeMap[str, DynArray[str]]
    skill_configs: TreeMap[str, SkillConfig]
    plugin_configs: TreeMap[str, PluginConfig]
    agent_memory: TreeMap[str, DynArray[MemoryEntry]]
    instruction_presets: TreeMap[str, Instruction]
    project_instructions: TreeMap[str, str]
    audit_log: DynArray[AuditEntry]
    skill_registry_addr: Address
    snippet_vault_addr: Address
    error_knowledge_addr: Address

    def __init__(self):
        self.owner = gl.message.sender_account
        self.version = "1.0.0"
        self.is_paused = False
        self._seed_builtin_skills()
        self._seed_builtin_plugins()

    @gl.public.write
    def create_project(self, name: str, description: str, stack: str) -> str:
        project_id = self._gen_id("proj")
        now = self._now()
        caller = str(gl.message.sender_account)
        p = Project(
            project_id=project_id,
            owner=caller,
            name=name,
            description=description,
            stack=stack,
            status="planning",
            created_at=now,
            updated_at=now,
            active_skill_ids=json.dumps(self._default_skills_for_stack(stack)),
            active_plugin_ids=json.dumps(["LinterPlugin", "CommentPlugin", "EnvPlugin"]),
            goal_ids=json.dumps([]),
            contributor_addresses=json.dumps([caller]),
            is_public=False,
            snapshot_count=u256(0),
        )
        self.projects[project_id] = p
        self.project_index.append(project_id)
        if caller not in self.user_projects:
            self.user_projects[caller] = DynArray[str]()
        self.user_projects[caller].append(project_id)
        self._log_audit("create_project", caller, project_id, f"Created project: {name}")
        return project_id

    @gl.public.view
    def get_project(self, project_id: str) -> dict:
        p = self.projects[project_id]
        return {
            "project_id": p.project_id,
            "owner": p.owner,
            "name": p.name,
            "description": p.description,
            "stack": p.stack,
            "status": p.status,
            "created_at": p.created_at,
            "updated_at": p.updated_at,
            "active_skills": json.loads(p.active_skill_ids),
            "active_plugins": json.loads(p.active_plugin_ids),
            "goal_ids": json.loads(p.goal_ids),
            "is_public": p.is_public,
        }

    @gl.public.write
    def add_contributor(self, project_id: str, contributor: str) -> None:
        self._assert_owner(project_id)
        p = self.projects[project_id]
        contributors = json.loads(p.contributor_addresses)
        if contributor not in contributors:
            contributors.append(contributor)
        p.contributor_addresses = json.dumps(contributors)
        self.projects[project_id] = p

    @gl.public.write
    def decompose_goal(self, project_id: str, goal_description: str) -> str:
        self._assert_contributor(project_id)
        p = self.projects[project_id]
        context = self._build_project_context(project_id)
        skills = json.loads(p.active_skill_ids)
        skill_fragments = self._get_skill_fragments(skills)
        prompt = f"""Decompose goal into JSON: {goal_description}"""
        def leader_fn():
            raw = gl.nondet.exec_prompt(prompt, response_format="json")
            return raw
        def validator_fn(leaders_res: gl.vm.Result) -> bool:
            return True
        result = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)
        goal_id = self._gen_id("goal")
        now = self._now()
        goal = Goal(
            goal_id=goal_id,
            project_id=project_id,
            description=goal_description,
            acceptance_criteria="Completed plan",
            task_ids=json.dumps([]),
            status="active",
            created_at=now,
        )
        self.goals[goal_id] = goal
        return goal_id

    @gl.public.write
    def generate_code(self, project_id: str, task_id: str) -> str:
        self._assert_contributor(project_id)
        task = self.tasks[task_id]
        prompt = f"""Generate code for {task.title}"""
        def leader_fn():
            return gl.nondet.exec_prompt(prompt, response_format="json")
        def validator_fn(leaders_res: gl.vm.Result) -> bool:
            return True
        result = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)
        return json.dumps([])

    @gl.public.write
    def debug_code(self, project_id: str, file_path: str, error_message: str) -> str:
        self._assert_contributor(project_id)
        return json.dumps({})

    @gl.public.write
    def generate_tests(self, project_id: str, target_file_path: str) -> str:
        self._assert_contributor(project_id)
        return json.dumps({})

    @gl.public.write
    def review_code(self, project_id: str, file_path: str) -> str:
        self._assert_contributor(project_id)
        return json.dumps({})

    @gl.public.write
    def generate_docs(self, project_id: str, doc_type: str) -> str:
        self._assert_contributor(project_id)
        return ""

    @gl.public.write
    def refactor_code(self, project_id: str, file_path: str, refactor_goal: str) -> str:
        self._assert_contributor(project_id)
        return ""

    @gl.public.write
    def translate_code(self, project_id: str, file_path: str, target_language: str) -> str:
        self._assert_contributor(project_id)
        return ""

    @gl.public.view
    def explain_code(self, project_id: str, file_path: str, detail_level: str) -> str:
        return ""

    @gl.public.write
    def activate_skill(self, project_id: str, skill_name: str) -> None:
        self._assert_contributor(project_id)

    @gl.public.write
    def deactivate_skill(self, project_id: str, skill_name: str) -> None:
        self._assert_contributor(project_id)

    @gl.public.view
    def list_skills(self) -> list:
        return list(self.skill_configs.keys())

    @gl.public.write
    def activate_plugin(self, project_id: str, plugin_name: str) -> None:
        self._assert_contributor(project_id)

    @gl.public.view
    def list_plugins(self) -> list:
        return list(self.plugin_configs.keys())

    @gl.public.write
    def save_instruction_preset(self, preset_name: str, system_prompt: str, temperature_hint: str, output_format: str) -> None:
        pass

    @gl.public.write
    def apply_instruction_preset(self, project_id: str, preset_name: str) -> None:
        self._assert_contributor(project_id)

    @gl.public.write
    def write_file_manual(self, project_id: str, path: str, language: str, content: str) -> None:
        self._assert_contributor(project_id)
        self._write_file(project_id, path, language, content, "Manual edit", str(gl.message.sender_account))

    @gl.public.write
    def delete_file(self, project_id: str, path: str) -> None:
        self._assert_contributor(project_id)

    @gl.public.view
    def read_file(self, project_id: str, path: str) -> dict:
        f = self.project_files[project_id][path]
        return {"path": f.path, "language": f.language, "content": f.content, "version": int(f.version), "updated_at": f.updated_at}

    @gl.public.view
    def list_files(self, project_id: str) -> list:
        try:
            files = self.project_files[project_id]
            result = []
            for path in files:
                f = files[path]
                if f.content != "__DELETED__":
                    result.append({"path": f.path, "language": f.language, "version": int(f.version), "updated_at": f.updated_at})
            return result
        except Exception:
            return []

    @gl.public.view
    def get_file_history(self, project_id: str, path: str) -> list:
        return []

    @gl.public.view
    def export_project_manifest(self, project_id: str) -> dict:
        project = self.projects[project_id]
        files = []
        return {"project": self.get_project(project_id), "files": files, "tasks": []}

    @gl.public.view
    def get_task(self, task_id: str) -> dict:
        t = self.tasks[task_id]
        return {"task_id": t.task_id, "title": t.title, "status": t.status}

    @gl.public.view
    def get_project_tasks(self, project_id: str) -> list:
        return []

    @gl.public.write
    def update_task_status(self, task_id: str, status: str, error_log: str) -> None:
        pass

    @gl.public.view
    def get_project_memory(self, project_id: str) -> list:
        return []

    @gl.public.write
    def add_memory_manual(self, project_id: str, content: str, category: str) -> None:
        self._assert_contributor(project_id)

    @gl.public.view
    def get_audit_log(self, limit: int) -> list:
        return []

    @gl.public.write
    def set_satellite_contract(self, contract_type: str, address: str) -> None:
        pass

    @gl.public.write
    def pause(self) -> None:
        self.is_paused = True

    def _assert_owner(self, project_id: str) -> None:
        pass

    def _assert_contributor(self, project_id: str) -> None:
        pass

    def _write_file(self, project_id: str, path: str, language: str, content: str, explanation: str, author: str) -> None:
        now = self._now()
        if project_id not in self.project_files:
            self.project_files[project_id] = TreeMap[str, CodeFile]()
        file = CodeFile(path=path, language=language, content=content, explanation=explanation, version=u256(1), created_at=now, updated_at=now, created_by=author, tags="")
        self.project_files[project_id][path] = file

    def _add_memory(self, project_id: str, content: str, category: str) -> None:
        pass

    def _build_project_context(self, project_id: str) -> str:
        return ""

    def _get_relevant_memory(self, project_id: str) -> str:
        return ""

    def _get_skill_fragments(self, skills: list) -> str:
        return ""

    def _get_plugin_instructions(self, plugins: list, trigger: str) -> str:
        return ""

    def _infer_test_framework(self, stack: str, language: str) -> str:
        return ""

    def _lookup_error_knowledge(self, error_message: str) -> str:
        return ""

    def _default_skills_for_stack(self, stack: str) -> list:
        return []

    def _handle_error(self, leaders_res: gl.vm.Result, leader_fn) -> bool:
        return True

    def _log_audit(self, action: str, actor: str, project_id: str, detail: str) -> None:
        pass

    def _gen_id(self, prefix: str) -> str:
        return prefix + "_1"

    def _now(self) -> str:
        return "block_1"

    def _seed_builtin_skills(self) -> None:
        pass

    def _seed_builtin_plugins(self) -> None:
        pass
