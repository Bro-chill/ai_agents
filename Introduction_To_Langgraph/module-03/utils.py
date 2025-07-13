from datetime import datetime

class Spy:
    def __init__(self):
        self.called_tools = []

    def __call__(self, run):
        q = [run]
        while q:
            r = q.pop()
            if r.child_runs:
                q.extend(r.child_runs)
            if r.run_type == "chat_model":
                self.called_tools.append(r.outputs["generations"][0][0]["message"]["kwargs"]["tool_calls"])

def extract_tool_info(tool_calls, schema_name="Memory"):
    """Extract information from tool calls for both patches and new memories.
    
    Args:
        tool_calls: List of tool calls from the model
        schema_name: Name of the schema tool (e.g., "Memory", "ToDo", "Profile")
    """
    changes = []
    
    for call_group in tool_calls:
        for call in call_group:
            if call['name'] == 'PatchDoc':
                changes.append({
                    'type': 'update',
                    'doc_id': call['args']['json_doc_id'],
                    'planned_edits': call['args']['planned_edits'],
                    'value': call['args']['patches'][0]['value']
                })
            elif call['name'] == schema_name:
                changes.append({
                    'type': 'new',
                    'value': call['args']
                })

    result_parts = []
    for change in changes:
        if change['type'] == 'update':
            result_parts.append(
                f"Document {change['doc_id']} updated:\n"
                f"Plan: {change['planned_edits']}\n"
                f"Added content: {change['value']}"
            )
        else:
            result_parts.append(
                f"New {schema_name} created:\n"
                f"Content: {change['value']}"
            )
    
    return "\n\n".join(result_parts)

def display_todo_list(store, user_id):
    """Display the current ToDo list in a formatted way."""
    namespace = ("todo", user_id)
    memories = store.search(namespace)
    
    if not memories:
        return "📝 **Current ToDo List:** Empty"
    
    todo_items = []
    for i, mem in enumerate(memories, 1):
        todo_data = mem.value
        task = todo_data.get('task', 'Unknown task')
        status = todo_data.get('status', 'not started')
        deadline = todo_data.get('deadline', 'No deadline')
        
        if deadline and deadline != 'No deadline':
            try:
                if isinstance(deadline, str):
                    deadline_str = deadline
                else:
                    deadline_str = deadline.strftime("%Y-%m-%d %H:%M")
            except:
                deadline_str = str(deadline)
        else:
            deadline_str = "No deadline"
            
        todo_items.append(f"   {i}. {task} - Status: {status} - Deadline: {deadline_str}")
    
    return "📝 **Current ToDo List:**\n" + "\n".join(todo_items)