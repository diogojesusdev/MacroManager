<script lang="ts">
  import TooltipWrapper from './../mycomponents/TooltipWrapper.svelte';
  import * as Table from '$lib/components/ui/table';
  import { Button } from '$lib/components/ui/button';
  import * as Dialog from '$lib/components/ui/dialog';
  import { Input } from '$lib/components/ui/input';
  import { Separator } from '$lib/components/ui/separator';

  import FaPython from 'svelte-icons/fa/FaPython.svelte';
  import FaPlus from 'svelte-icons/fa/FaPlus.svelte';
  import FaPlay from 'svelte-icons/fa/FaPlay.svelte';
  import MdFolder from 'svelte-icons/md/MdFolder.svelte';
  import FaCode from 'svelte-icons/fa/FaCode.svelte';
  import FaFileAlt from 'svelte-icons/fa/FaFileAlt.svelte';
  import FaClock from 'svelte-icons/fa/FaClock.svelte';
  import FaRedo from 'svelte-icons/fa/FaRedo.svelte';
  import TaskSchedulerDialog from '../mycomponents/TaskSchedulerDialog.svelte';
  import { onMount } from 'svelte';
  import { executeRPC } from '$lib/BackendRPCs';
  import TaskCreatorDialog from '../mycomponents/TaskCreatorDialog.svelte';
  import MacroExecutionDialogContent from '../mycomponents/MacroExecutionDialogContent.svelte';
  import { Loader } from 'lucide-svelte';
  import type IMacroManager from '$lib/types/IMacroManager';

  let isRefreshing = false;
  let macros: Array<
    Omit<ReturnType<IMacroManager['get_macros_flat']>[number], 'last_run'> & {
      last_run: Date;
    }
  > = [];

  let frameworkVersionInfo: ReturnType<
    IMacroManager['get_framework_versions']
  > | null = null;
  let shouldUpdateManager: boolean | null = null;
  let isUpdatingManager = false;
  let isUpdatingFramework = false;

  let filterText: string | null = null;
  $: macrosFiltered = filterText
    ? macros.filter((m) =>
        m.name.toLowerCase().includes(filterText.toLowerCase())
      )
    : null;

  async function executeLogsRPC(
    absoluteMacroPath: string
  ): Promise<Array<string>> {
    return new Promise((res) =>
      executeRPC('get_latest_macro_logs', [absoluteMacroPath], res)
    );
  }

  async function refreshFlatMacroList(userIntention: boolean = false) {
    if (isRefreshing) return;
    // Avoid flickering animation
    let iv;
    if (!userIntention) iv = setTimeout(() => (isRefreshing = true), 300);
    else isRefreshing = true;

    await executeRPC('get_macros_flat', [], (result) => {
      macros = result.map((macro) => ({
        ...macro,
        last_run: !macro.last_run ? undefined : new Date(macro.last_run),
      }));
    });

    if (iv) clearTimeout(iv);
    setTimeout(() => (isRefreshing = false), 500);
  }

  function updateFramework() {
    if (!frameworkVersionInfo.should_update) return;

    isUpdatingFramework = true;

    executeRPC('update_framework', [], () => {
      executeRPC('get_framework_versions', [], (result) => {
        frameworkVersionInfo = result;
        isUpdatingFramework = false;
      });
    });
  }

  function updateManager() {
    if (!shouldUpdateManager) return;

    isUpdatingManager = true;

    setTimeout(window.location.reload, 4000);
    executeRPC('update_manager', []);
  }

  onMount(() => {
    refreshFlatMacroList();
    setInterval(() => refreshFlatMacroList(), 5000);

    executeRPC('get_framework_versions', [], (result) => {
      frameworkVersionInfo = result;
    });

    executeRPC('should_update_manager', [], (result) => {
      shouldUpdateManager = result;
    });
  });
</script>

<h1 class="my-0 ml-0">Macro Manager</h1>

<p class="my-6 text-lg text-slate-200">
  Manages your macros located at <code>%userprofile%\MacroManager</code>
</p>

<div id="lib_update_buttons" class="flex items-center justify-start gap-3 mb-4">
  {#if frameworkVersionInfo == null}
    <Loader />
  {:else}
    <Button
      on:click={updateFramework}
      disabled={!frameworkVersionInfo.should_update || isUpdatingFramework}
      class={frameworkVersionInfo.should_update
        ? 'bg-red-600 hover:bg-red-500'
        : `bg-green-600 hover:bg-green-500`}
      variant="outline"
    >
      {#if frameworkVersionInfo.should_update}
        Framework Update! {frameworkVersionInfo.current_version} => {frameworkVersionInfo.remote_version}
      {:else}
        Framework Version: {frameworkVersionInfo.current_version}
      {/if}
    </Button>
  {/if}

  {#if shouldUpdateManager == null}
    <Loader />
  {:else}
    <Button
      disabled={!shouldUpdateManager || isUpdatingManager}
      on:click={updateManager}
      class={shouldUpdateManager
        ? 'bg-red-600 hover:bg-red-500'
        : `bg-green-600 hover:bg-green-500`}
      variant="outline"
    >
      {#if shouldUpdateManager}
        Macro Manager Update!
      {:else}
        Macro Manager Up To Date!
      {/if}
    </Button>
  {/if}
</div>

<div id="macro_buttons" class="flex items-center justify-start gap-3">
  <Button
    variant="secondary"
    class="my-4 bg-yellow-700 hover:bg-yellow-600"
    on:click={() => executeRPC('open_macros_folder', [])}
  >
    <span class="mr-3 icon">
      <MdFolder />
    </span>
    Open Macros Folder
  </Button>

  <Button
    variant="secondary"
    class="my-4 bg-blue-500 hover:bg-blue-400"
    on:click={() => executeRPC('open_macro_template', [])}
  >
    <span class="mr-3 icon">
      <FaPython />
    </span>
    Open Macro Template
  </Button>
</div>

<div id="macro_buttons_2" class="flex items-center justify-start gap-3">
  <TaskCreatorDialog refreshList={refreshFlatMacroList}>
    <Button variant="secondary" class="bg-green-600 hover:bg-green-500">
      <span class="mr-3 icon">
        <FaPlus />
      </span>
      New
    </Button>
  </TaskCreatorDialog>

  <Button
    variant="secondary"
    class="bg-blue-800 hover:bg-blue-700"
    disabled={isRefreshing}
    on:click={() => refreshFlatMacroList(true)}
  >
    <span class="mr-3 icon">
      <FaRedo />
    </span>
    {isRefreshing ? 'Refreshing' : 'Refresh'}
  </Button>
</div>

<Input
  class="max-w-sm my-3 border-[3px]"
  placeholder="Filter by name ..."
  type="text"
  bind:value={filterText}
/>

<div class="border-2 rounded-md">
  <Table.Root>
    <Table.Header>
      <Table.Row>
        <Table.Head />
        <Table.Head>Name</Table.Head>
        <Table.Head>Path</Table.Head>
        <Table.Head>Last Run</Table.Head>
      </Table.Row>
    </Table.Header>
    <Table.Body>
      {#each macrosFiltered || macros as macro}
        <Table.Row>
          <Table.Cell>
            <Dialog.Root closeOnOutsideClick={false} closeOnEscape={false}>
              <Dialog.Trigger>
                <!-- svelte-ignore a11y-no-static-element-interactions -->
                <TooltipWrapper msg="Run Macro">
                  <!-- svelte-ignore a11y-click-events-have-key-events -->
                  <!-- Clicking opens dialog to choose invocation variables -->
                  <span class="text-green-500 icon">
                    <FaPlay />
                  </span>
                </TooltipWrapper>
              </Dialog.Trigger>
              <Dialog.DialogContent class="min-w-[50vw]">
                <Dialog.Header>
                  <Dialog.Title class="text-2xl"
                    >Run "{macro.name}"</Dialog.Title
                  >
                  <Dialog.Description>
                    Runs your macro with invocation variables set by you
                  </Dialog.Description>
                  <MacroExecutionDialogContent macroPath={macro.path} />
                </Dialog.Header>
              </Dialog.DialogContent>
            </Dialog.Root>
          </Table.Cell>

          <Table.Cell class="text-lg font-bold text-slate-300"
            >{macro.name}</Table.Cell
          >
          <Table.Cell class="text-sm">{macro.path}</Table.Cell>
          <Table.Cell class="flex items-center justify-start gap-4">
            {macro.last_run ? macro.last_run.toUTCString() : 'N/A'}
            {#if macro.last_run}
              <Dialog.Root closeOnOutsideClick={false} closeOnEscape={false}>
                <Dialog.Trigger>
                  <!-- svelte-ignore a11y-click-events-have-key-events -->
                  <TooltipWrapper msg="See Last Run Logs">
                    <!-- svelte-ignore a11y-click-events-have-key-events -->
                    <!-- svelte-ignore a11y-no-static-element-interactions -->
                    <span class="text-slate-300 icon">
                      <FaFileAlt />
                    </span>
                  </TooltipWrapper>
                </Dialog.Trigger>
                <Dialog.DialogContent class="min-w-[90vw] pt-14">
                  <div id="logs" class="overflow-auto max-h-[80vh]">
                    {#await executeLogsRPC(macro.path)}
                      <p>Loading Logs for {macro.path}...</p>
                    {:then log_lines}
                      {#each log_lines as log_line, idx}
                        {#if idx < log_lines.length}
                          <Separator
                            class="my-1 border-2"
                            orientation="horizontal"
                          />
                        {/if}
                        <div class="w-[90%] py-1">
                          {log_line}
                        </div>
                      {/each}
                    {:catch}
                      <p>
                        Could not load Logs for {macro.path}! Try to go to the
                        Logs folder manually
                      </p>
                    {/await}
                  </div>
                </Dialog.DialogContent>
              </Dialog.Root>
            {/if}
          </Table.Cell>

          <Table.Cell>
            <!-- svelte-ignore a11y-no-static-element-interactions -->
            <TooltipWrapper msg="Open in File Explorer">
              <!-- svelte-ignore a11y-click-events-have-key-events -->
              <span
                class="text-yellow-400 icon"
                on:click={() =>
                  executeRPC('open_macro_in_file_explorer', [macro.path])}
              >
                <MdFolder />
              </span>
            </TooltipWrapper>
          </Table.Cell>

          <Table.Cell>
            <!-- svelte-ignore a11y-click-events-have-key-events -->
            <TooltipWrapper msg="Open in Code Editor">
              <!-- svelte-ignore a11y-click-events-have-key-events -->
              <!-- svelte-ignore a11y-no-static-element-interactions -->
              <span
                class="text-blue-500 icon"
                on:click={() =>
                  executeRPC('open_macro_in_code_editor', [macro.path])}
              >
                <FaCode />
              </span>
            </TooltipWrapper>
          </Table.Cell>

          <Table.Cell>
            <TooltipWrapper msg="Schedule">
              <!-- svelte-ignore a11y-no-static-element-interactions -->
              <TaskSchedulerDialog macroPath={macro.path}>
                <!-- svelte-ignore a11y-click-events-have-key-events -->
                <span class="icon text-zinc-400">
                  <FaClock />
                </span>
              </TaskSchedulerDialog>
            </TooltipWrapper>
          </Table.Cell>
        </Table.Row>
      {/each}
    </Table.Body>
  </Table.Root>
</div>
