use tauri::AppHandle;
use tauri_plugin_shell::ShellExt;

pub async fn call_backend(app: &AppHandle, action: &str, args: &[&str]) -> Result<String, String> {
    let mut command = app
        .shell()
        .sidecar("claudeminder-sidecar")
        .map_err(|e| e.to_string())?
        .arg(action);

    for arg in args {
        command = command.arg(*arg);
    }

    let output = command.output().await.map_err(|e| e.to_string())?;

    if output.status.success() {
        Ok(String::from_utf8_lossy(&output.stdout).to_string())
    } else {
        let stderr = String::from_utf8_lossy(&output.stderr).to_string();
        if stderr.is_empty() {
            Err("Sidecar execution failed".to_string())
        } else {
            Err(stderr)
        }
    }
}
