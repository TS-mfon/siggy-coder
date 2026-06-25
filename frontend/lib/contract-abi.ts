export const SIGGY_CODER_ABI = [
  {
    "name": "create_project",
    "type": "function",
    "stateMutability": "nonpayable",
    "inputs": [
      {"name": "name", "type": "string"},
      {"name": "description", "type": "string"},
      {"name": "stack", "type": "string"}
    ],
    "outputs": [{"type": "string"}]
  },
  {
    "name": "get_project",
    "type": "function",
    "stateMutability": "view",
    "inputs": [{"name": "project_id", "type": "string"}],
    "outputs": [{"type": "tuple", "components": [
      {"name": "project_id", "type": "string"},
      {"name": "owner", "type": "string"},
      {"name": "name", "type": "string"},
      {"name": "description", "type": "string"},
      {"name": "stack", "type": "string"},
      {"name": "status", "type": "string"},
      {"name": "created_at", "type": "string"},
      {"name": "updated_at", "type": "string"},
      {"name": "active_skills", "type": "string[]"},
      {"name": "active_plugins", "type": "string[]"},
      {"name": "goal_ids", "type": "string[]"},
      {"name": "is_public", "type": "bool"}
    ]}]
  },
  {
    "name": "decompose_goal",
    "type": "function",
    "stateMutability": "nonpayable",
    "inputs": [
      {"name": "project_id", "type": "string"},
      {"name": "goal_description", "type": "string"}
    ],
    "outputs": [{"type": "string"}]
  },
  {
    "name": "generate_code",
    "type": "function",
    "stateMutability": "nonpayable",
    "inputs": [
      {"name": "project_id", "type": "string"},
      {"name": "task_id", "type": "string"}
    ],
    "outputs": [{"type": "string"}]
  },
  {
    "name": "read_file",
    "type": "function",
    "stateMutability": "view",
    "inputs": [
      {"name": "project_id", "type": "string"},
      {"name": "path", "type": "string"}
    ],
    "outputs": [{"type": "tuple", "components": [
      {"name": "path", "type": "string"},
      {"name": "language", "type": "string"},
      {"name": "content", "type": "string"},
      {"name": "version", "type": "uint256"},
      {"name": "updated_at", "type": "string"}
    ]}]
  },
  {
    "name": "list_files",
    "type": "function",
    "stateMutability": "view",
    "inputs": [{"name": "project_id", "type": "string"}],
    "outputs": [{"type": "tuple[]", "components": [
      {"name": "path", "type": "string"},
      {"name": "language", "type": "string"},
      {"name": "version", "type": "uint256"},
      {"name": "updated_at", "type": "string"}
    ]}]
  },
  {
    "name": "get_project_tasks",
    "type": "function",
    "stateMutability": "view",
    "inputs": [{"name": "project_id", "type": "string"}],
    "outputs": [{"type": "tuple[]", "components": [
      {"name": "task_id", "type": "string"},
      {"name": "title", "type": "string"},
      {"name": "description", "type": "string"},
      {"name": "assigned_agent", "type": "string"},
      {"name": "status", "type": "string"},
      {"name": "priority", "type": "string"},
      {"name": "depends_on", "type": "string[]"},
      {"name": "output_files", "type": "string[]"},
      {"name": "error_log", "type": "string"},
      {"name": "retry_count", "type": "uint256"}
    ]}]
  },
  {
    "name": "get_project_memory",
    "type": "function",
    "stateMutability": "view",
    "inputs": [{"name": "project_id", "type": "string"}],
    "outputs": [{"type": "tuple[]", "components": [
      {"name": "content", "type": "string"},
      {"name": "category", "type": "string"},
      {"name": "timestamp", "type": "string"}
    ]}]
  },
  {
    "name": "export_project_manifest",
    "type": "function",
    "stateMutability": "view",
    "inputs": [{"name": "project_id", "type": "string"}],
    "outputs": [{"type": "tuple", "components": [
      {"name": "project", "type": "tuple", "components": [
        {"name": "project_id", "type": "string"},
        {"name": "name", "type": "string"}
      ]},
      {"name": "files", "type": "tuple[]", "components": [
        {"name": "path", "type": "string"},
        {"name": "language", "type": "string"},
        {"name": "content", "type": "string"}
      ]},
      {"name": "tasks", "type": "tuple[]", "components": [
        {"name": "id", "type": "string"},
        {"name": "title", "type": "string"},
        {"name": "status", "type": "string"},
        {"name": "agent", "type": "string"}
      ]}
    ]}]
  }
];
export const SNIPPET_VAULT_ABI = [];
export const ERROR_KNOWLEDGE_ABI = [];
export const TEMPLATE_VAULT_ABI = [];
export const PROJECT_FACTORY_ABI = [];