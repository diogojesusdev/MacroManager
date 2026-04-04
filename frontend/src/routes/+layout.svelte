<script lang="ts">
  import '../app.postcss';
  import * as Alert from '$lib/components/ui/alert';
  import { onMount } from 'svelte';

  let popup: {
    title: string;
    message: string;
  } | null = null;

  onMount(() => {
    (window as any).message = (
      title: string,
      message: string,
      delay_s: number
    ) => {
      popup = { title, message };
      setTimeout(() => (popup = null), delay_s * 1000);
    };
  });
</script>

{#if popup}
  <div class="fixed z-50 flex items-start justify-center w-full">
    <div class="max-w-full top-10">
      <Alert.Root class="border-2 border-white">
        <Alert.Title class="text-xl">{popup.title}</Alert.Title>
        <Alert.Description class="text-lg">
          {popup.message}
        </Alert.Description>
      </Alert.Root>
    </div>
  </div>
{/if}

<slot />
