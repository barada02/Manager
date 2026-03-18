import os


def mask_key_preview(secret: str) -> str:
	if len(secret) <= 8:
		return "*" * len(secret)
	return f"{secret[:6]}...{secret[-4:]}"


def get_required_env_var(var_name: str) -> str:
	try:
		value = os.environ[var_name].strip()
		if not value:
			raise ValueError(f"{var_name} is empty")
		print(f"[Auth Check] {var_name} loaded: {mask_key_preview(value)}")
		return value
	except Exception as exc:
		print(f"[Auth Check] Error reading {var_name}: {exc}")
		raise RuntimeError(
			f"{var_name} is missing/invalid in runtime environment. "
			"Set it in .gradient/agent.yml under env_vars and redeploy."
		) from exc
