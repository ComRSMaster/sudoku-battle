<script lang="ts">
	import { onMount } from 'svelte';

	interface LeaderboardPosition {
		rank: number;
		user_id: number;
		solved_count: number;
	}

	let position = $state<LeaderboardPosition | null>(null);
	let loading = $state(true);
	let userId = 1; // TODO

	async function loadUserPosition() {
		try {
			loading = true;
			const response = await fetch(`/api/leaderboards/user/${userId}`);
			const data = await response.json();
			position = data;
		} catch (error) {
			console.error('Failed to load user position:', error);
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		loadUserPosition();
	});
</script>

<div class="flex h-full flex-col p-5">
	<div class="mb-5">
		<p class="text-sm font-semibold tracking-[0.16em] uppercase opacity-60">Profile</p>
	</div>

	{#if loading}
		<div class="flex items-center justify-center">
			<p class="text-sm opacity-60">Загрузка профиля...</p>
		</div>
	{:else if position}
		<div class="card preset-filled-primary-500 p-5">
			<p class="text-sm tracking-[0.16em] uppercase opacity-70">Player Card</p>
			<h2 class="mt-2 text-3xl font-black">User {position.user_id}</h2>
			<p class="mt-1 text-sm opacity-80">Ранг: #{position.rank}</p>
		</div>

		<div class="mt-5 grid grid-cols-2 gap-3">
			<div class="card preset-outlined-surface-200-800 p-4">
				<p class="text-xs tracking-[0.16em] uppercase opacity-50">Разгадано</p>
				<p class="mt-2 text-3xl font-black">{position.solved_count}</p>
			</div>
			<div class="card preset-outlined-surface-200-800 p-4">
				<p class="text-xs tracking-[0.16em] uppercase opacity-50">Позиция</p>
				<p class="mt-2 text-3xl font-black">#{position.rank}</p>
			</div>
		</div>

		<div class="mt-5 card preset-filled p-4">
			<p class="font-semibold">Ваша статистика</p>
			<p class="mt-1 text-sm opacity-65">
				Вы разгадали {position.solved_count} судоку и занимаете {position.rank}-е место в
				лидербордe.
			</p>
		</div>
	{/if}
</div>
