from contextvars import ContextVar

# 定义全局的 ContextVar，用于存储 trace_id
trace_id_var: ContextVar[str | None] = ContextVar('trace_id', default=None)

# 定义全局的 ContextVar，用于存储 user_id
user_id_var: ContextVar[int] = ContextVar('user_id', default=0)
