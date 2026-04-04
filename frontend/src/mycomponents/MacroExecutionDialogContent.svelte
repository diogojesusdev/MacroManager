<script lang="ts">
  import { executeRPC, validateMacroRPC } from '$lib/BackendRPCs';
  import Button from '$lib/components/ui/button/button.svelte';
  import { Input } from '$lib/components/ui/input';
  import Label from '$lib/components/ui/label/label.svelte';
  import { onMount } from 'svelte';
  import InvocationVariablesForm from './InvocationVariablesForm.svelte';
  import type {
    InvocationVariables,
    InvocationVariablesMetadata,
  } from '$lib/types/MacroDerivedTypes';
  import { Checkbox, Toggle } from 'bits-ui';
  import { Check, Minus } from 'lucide-svelte';

  export let macroPath: string;

  const clearErrorTimeS = 5;
  let errorInterval: any;
  let errorMessage: string | null = null;
  let autoRun: boolean = false;
  let exitAfterRun: boolean = false;

  let invocationVariablesMetadata:
    | 'loading'
    | null
    | InvocationVariablesMetadata = 'loading';

  let invocationVariablesValues: InvocationVariables = {};
  let timeBetweenInstructionsS: string = '1';

  function getInvocationVariablesMD(): Promise<null | InvocationVariablesMetadata> {
    return new Promise((res) =>
      executeRPC(
        'get_macro_invocation_variables_metadata',
        [macroPath],
        (data) => {
          res(Object.keys(data).length == 0 ? null : data);
        }
      )
    );
  }

  function showError(message: string) {
    errorMessage = message;

    errorInterval = setTimeout(
      () => (errorMessage = null),
      clearErrorTimeS * 1000
    );
  }

  function runMacro() {
    if (invocationVariablesMetadata == 'loading') return;

    if (errorInterval) clearInterval(errorInterval);
    errorMessage = null;

    const result = validateMacroRPC(
      invocationVariablesMetadata,
      invocationVariablesValues
    );

    if (result != 'valid') {
      showError(result.message);
      return;
    }

    executeRPC('run_macro', [
      macroPath,
      invocationVariablesValues,
      timeBetweenInstructionsS,
      autoRun,
      exitAfterRun,
    ]);
  }

  onMount(
    async () => (invocationVariablesMetadata = await getInvocationVariablesMD())
  );
</script>

<div class="flex flex-col gap-1 pt-4">
  {#if errorMessage}
    <p class="mb-6 text-lg font-bold text-red-600">ERROR: {errorMessage}</p>
  {/if}

  <Label class="mb-3 text-lg underline underline-offset-4"
    >Interval Between Operations</Label
  >
  <span class="flex items-center gap-3 mb-3">
    <Input
      value="1"
      class="w-28"
      type="number"
      on:input={(e) => (timeBetweenInstructionsS = e.currentTarget.value)}
    />
    seconds
  </span>

  <span class="flex items-center gap-3 mb-3">
    <Checkbox.Root
      id="terms"
      aria-labelledby="terms-label"
      class="peer inline-flex size-[25px] items-center justify-center rounded-md border border-muted bg-foreground transition-all duration-150 ease-in-out active:scale-98 data-[state=unchecked]:border-border-input data-[state=unchecked]:bg-background data-[state=unchecked]:hover:border-dark-40"
      onCheckedChange={(v) => (autoRun = Boolean(v))}
      checked={autoRun}
    >
      <Checkbox.Indicator
        class="inline-flex items-center justify-center text-background"
      >
        <Check class="size-[15px]" />
      </Checkbox.Indicator>
    </Checkbox.Root>
    Auto-Run
  </span>

  <span class="flex items-center gap-3 mb-3">
    <Checkbox.Root
      id="terms"
      aria-labelledby="terms-label"
      class="peer inline-flex size-[25px] items-center justify-center rounded-md border border-muted bg-foreground transition-all duration-150 ease-in-out active:scale-98 data-[state=unchecked]:border-border-input data-[state=unchecked]:bg-background data-[state=unchecked]:hover:border-dark-40"
      onCheckedChange={(v) => (exitAfterRun = Boolean(v))}
      checked={exitAfterRun}
    >
      <Checkbox.Indicator
        class="inline-flex items-center justify-center text-background"
      >
        <Check class="size-[15px]" />
      </Checkbox.Indicator>
    </Checkbox.Root>
    Exit After Run
  </span>

  <InvocationVariablesForm
    {invocationVariablesMetadata}
    {invocationVariablesValues}
  />

  <br />

  <Button
    class="bg-green-600 hover:bg-green-500 text-slate-200"
    on:click={runMacro}
  >
    Run
  </Button>
</div>
