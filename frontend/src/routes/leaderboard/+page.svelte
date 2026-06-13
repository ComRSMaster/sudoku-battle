<script lang="ts">
	import { onMount } from 'svelte';
	import { API_BASE } from '$lib/config';
	import { getTmaInitData } from '$lib/tma';

	interface LeaderboardEntry {
		rank: number;
		user_id: number;
		solved_count: number;
	}

	let leaderboard = $state<LeaderboardEntry[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	async function loadLeaderboard() {
		try {
			loading = true;
			const response = await fetch(`${API_BASE}/api/leaderboards/?limit=100&tma=${getTmaInitData()}`);
			const data = await response.json();
			leaderboard = data.leaderboard;
			error = null;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load leaderboard';
			console.error('Failed to load leaderboard:', err);
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		loadLeaderboard();
		const interval = setInterval(loadLeaderboard, 30000);
		return () => clearInterval(interval);
	});
</script>

<div class="flex h-full flex-col p-5">
	<div class="mb-5">
		<p class="text-sm font-semibold tracking-[0.16em] uppercase opacity-60">Leaderboard</p>
	</div>

	<div class="space-y-3">
		<h2 class="text-3xl font-black">Лучшие игроки</h2>
		<p class="text-sm opacity-65">Топ игроков по количеству разгаданных судоку.</p>
	</div>

	{#if loading}
		<div class="mt-6 flex items-center justify-center">
			<p class="text-sm opacity-60">Загрузка лидерборда...</p>
		</div>
	{:else if error}
		<div class="mt-6 flex items-center justify-center">
			<p class="text-sm text-red-500">Ошибка: {error}</p>
		</div>
	{:else if leaderboard.length === 0}
		<div class="mt-6 flex items-center justify-center">
			<p class="text-sm opacity-60">Лидерборд пуст</p>
		</div>
	{:else}
		<div class="mt-6 space-y-3">
			{#each leaderboard as player (player.user_id)}
				<div class="flex items-center justify-between card preset-outlined-surface-200-800 p-4">
					<div class="flex items-center gap-4">
						<div
							class="flex h-10 w-10 items-center justify-center rounded-xl preset-filled-primary-500 font-black"
						>
							{player.rank}
						</div>
						<div>
							<p class="font-bold">User {player.user_id}</p>
							<p class="text-sm opacity-60">{player.solved_count} разгадано</p>
						</div>
					</div>
					<div class="text-right">
						<p class="text-lg font-black">{player.solved_count}</p>
						<p class="text-xs tracking-[0.14em] uppercase opacity-50">Игр</p>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>
