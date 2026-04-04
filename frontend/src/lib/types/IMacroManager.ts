export default interface IMacroManager 
{
    create_macro(macro_name: string): string;
    get_framework_versions(): {
    should_update: boolean;
    current_version: string;
    remote_version: string;
}
;
    get_latest_macro_logs(absolute_macro_path: string): Array<string>;
    get_macro_invocation_variables_metadata(absolute_macro_path: string): {
    variables: Record<string, {
    type: string;
    accepted_values: Array<string> | null;
}
>;
}
;
    get_macros_flat(): Array<{
    name: string;
    path: string;
    last_run: string | null;
}
>;
    open_macro_in_code_editor(absolute_macro_path: string): void;
    open_macro_in_file_explorer(absolute_macro_path: string): void;
    open_macro_template(): void;
    open_macros_folder(): void;
    open_task_scheduler(): void;
    run_macro(absolute_macro_path: string, invocation_variables: Record<string, string>, time_between_instructions_s: string | null, auto_run: boolean, exit_after_run: boolean): void;
    should_update_manager(): boolean;
    update_framework(): void;
    update_manager(): void;
}
