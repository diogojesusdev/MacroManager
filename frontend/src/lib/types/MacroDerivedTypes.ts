import type IMacroManager from "./IMacroManager";

export type InvocationVariables = Parameters<IMacroManager['run_macro']>[1]
export type InvocationVariablesMetadata = ReturnType<
    IMacroManager['get_macro_invocation_variables_metadata']
>