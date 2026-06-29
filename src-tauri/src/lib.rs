use std::sync::Mutex;

struct SidecarChild(Mutex<Option<tauri_plugin_shell::process::CommandChild>>);

impl Drop for SidecarChild {
    fn drop(&mut self) {
        if let Ok(mut guard) = self.0.lock() {
            if let Some(child) = guard.take() {
                let _ = child.kill();
            }
        }
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .setup(|app| {
            #[cfg(not(debug_assertions))]
            {
                use tauri_plugin_shell::ShellExt;
                let shell = app.shell();
                let sidecar_command = shell
                    .sidecar("pdfoo-server")
                    .expect("failed to create sidecar command");
                let (_rx, child) = sidecar_command
                    .spawn()
                    .expect("failed to spawn sidecar");
                app.manage(SidecarChild(Mutex::new(Some(child))));
            }

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
