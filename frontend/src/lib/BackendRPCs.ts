import type IMacroManager from "./types/IMacroManager";
import type { InvocationVariables, InvocationVariablesMetadata } from "./types/MacroDerivedTypes";

export type ErrorMessage = string

export function validateMacroRPC(
	invocationVariablesMetadata: InvocationVariablesMetadata | null,
	invocationVariablesValues: InvocationVariables
): "valid" | Error {
	if (invocationVariablesMetadata == null)
		return "valid"

	if (
		Object.keys(invocationVariablesValues).length !=
		Object.keys(invocationVariablesMetadata.variables).length
	) {
		return Error('Some variables are missing. You need to provide a value for all the variables')
	}

	const typeErrorsMsgs = [];
	for (const [varname, value] of Object.entries(invocationVariablesValues)) {
		const { type, accepted_values } = invocationVariablesMetadata.variables[varname];

		if (accepted_values != null) continue; // these should be autocomplete making it imposible to have invalid value

		if (type == 'number') {
			if (value.includes(' ') || isNaN(parseFloat(value))) {
				typeErrorsMsgs.push(`${varname} must be a number`);
			}
		}
	}
	if (typeErrorsMsgs.length > 0) {
		return Error(typeErrorsMsgs.join('; '))
	}

	return "valid"
}

export async function executeRPC<K extends keyof IMacroManager>(
	rpcName: K,
	args: Parameters<IMacroManager[K]>,
	onSuccess?: (data: Awaited<ReturnType<IMacroManager[K]>>) => void,
	onError?: (error_msg: string) => void
): Promise<void> {
	try {
		const res = await fetch('http://localhost:8181/rpc', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({
				fn: rpcName,
				args: args,
			}),
		})

		const jsonBody = await res.json()

		if (jsonBody.error) {
			(window as any).message("Error", jsonBody.error_msg, 7)
			onError?.(jsonBody.error_msg)
		} else {
			onSuccess?.(jsonBody.data)
		}
	} catch (e) {
		console.error("Could not connect to backend: " + e)
	}
}