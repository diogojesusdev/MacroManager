<script lang="ts">
  import * as Dialog from '$lib/components/ui/dialog';
  import { Button } from '$lib/components/ui/button';
  import Label from '$lib/components/ui/label/label.svelte';
  import { Input } from '$lib/components/ui/input';
  import { executeRPC } from '$lib/BackendRPCs';

  export let refreshList: () => void;

  let macroName: string;
  let macroCreated = false;
  let macroPath: string;

  const closeDialogBtnSelector =
    '#create-macro-dialog [data-melt-dialog-close]';

  function createMacro() {
    if (macroCreated) return;

    executeRPC(
      'create_macro',
      [macroName],
      (mp) => {
        macroCreated = true;
        macroPath = mp;

        document
          .querySelector(closeDialogBtnSelector)
          .addEventListener('click', () => {
            macroName = '';
            macroCreated = false;
            macroPath = '';

            // Refresh outside list
            refreshList();
          });
      },
      () => {
        // Click outside to see the error popup
        (
          document.querySelector(closeDialogBtnSelector) as HTMLButtonElement
        ).click();
      }
    );
  }
</script>

<div>
  <Dialog.Root closeOnOutsideClick={false} closeOnEscape={false}>
    <Dialog.Trigger>
      <slot />
    </Dialog.Trigger>

    <Dialog.DialogContent id="create-macro-dialog" class="min-w-[50vw]">
      <Dialog.Header>
        <Dialog.Title class="text-2xl">Create Macro</Dialog.Title>
        <Dialog.Description
          >1. Creates folder: <code
            >%userprofile%\MacroManager\{'<MACRO_NAME>'}</code
          >
          <br />
          2. Creates a python file with a macro template: (<code>macro.py</code
          >)
        </Dialog.Description>
      </Dialog.Header>
      <div class="flex flex-col justify-center gap-3">
        <br />
        {#if !macroCreated}
          <Label>Macro Name</Label>
          <Input bind:value={macroName} />
          <Button
            on:click={createMacro}
            class="text-white bg-green-500 hover:bg-green-400">Create</Button
          >
        {:else}
          <Label class="text-lg">Macro "{macroName}" created at:</Label>
          <code>{macroPath}</code>
          <Button
            on:click={() =>
              executeRPC('open_macro_in_file_explorer', [macroPath])}
            class="text-white bg-green-500 hover:bg-green-400"
            >Open in file explorer</Button
          >

          <Button
            on:click={() =>
              executeRPC('open_macro_in_code_editor', [macroPath])}
            class="text-white bg-blue-600 hover:bg-blue-500"
            >Open in Code Editor</Button
          >
        {/if}
      </div>
    </Dialog.DialogContent>
  </Dialog.Root>
</div>
