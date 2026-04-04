<script lang="ts">
  import * as Tooltip from '$lib/components/ui/tooltip';

  export let msg: string;
</script>

<Tooltip.Root>
  <Tooltip.Trigger>
    <slot />
  </Tooltip.Trigger>

  <Tooltip.Content>{msg}</Tooltip.Content>
</Tooltip.Root>
