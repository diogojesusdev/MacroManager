<script lang="ts">
  import { Input } from '$lib/components/ui/input';
  import Label from '$lib/components/ui/label/label.svelte';
  import * as Select from '$lib/components/ui/select';
  import type {
    InvocationVariables,
    InvocationVariablesMetadata,
  } from '$lib/types/MacroDerivedTypes';

  export let invocationVariablesMetadata:
    | 'loading'
    | null
    | InvocationVariablesMetadata = 'loading';
  export let invocationVariablesValues: InvocationVariables = {};
  export let onChange: () => void = () => {};
</script>

{#if invocationVariablesMetadata == 'loading'}
  <p>Loading...</p>
{:else if invocationVariablesMetadata != null}
  {#if invocationVariablesMetadata}
    <Label class="text-lg underline underline-offset-4">
      Invocation Variables
    </Label>

    <div
      id="invocation-variables"
      class="flex flex-col gap-1 max-h-[80vh] overflow-y-auto"
    >
      {#each Object.entries(invocationVariablesMetadata.variables) as [varname, { type, accepted_values }]}
        <div class="flex items-center gap-3 variable">
          <div class="flex items-center gap-1 border-1">
            <span />
            {varname} <code> ({type})</code>
          </div>

          {#if accepted_values}
            <Select.Root portal={null}>
              <Select.Trigger class="border-2">
                <Select.Value placeholder="Select a value" />
              </Select.Trigger>
              <Select.Content>
                <Select.Group>
                  {#each accepted_values as accepted_value}
                    <Select.Item
                      on:click={() => {
                        invocationVariablesValues[varname] = accepted_value;
                        onChange();
                      }}
                      class="py-2"
                      value={accepted_value}
                      label={accepted_value}>{accepted_value}</Select.Item
                    >
                  {/each}
                </Select.Group>
              </Select.Content>
            </Select.Root>
          {:else}
            <Input
              class="border-2"
              on:input={(e) => {
                invocationVariablesValues[varname] = e.currentTarget.value;
                onChange();
              }}
            />
          {/if}
          <br />
        </div>
      {/each}
    </div>
  {/if}
{/if}
