<script lang="ts">
	import { onMount } from 'svelte';
	import { PlayIcon, TrophyIcon, UserRoundIcon } from '@lucide/svelte';
	import { API_BASE } from '$lib/config';
	import { getTmaInitData } from '$lib/tma';

	let history = $state<{ game_id: number; created_at: string }[]>([]);
	onMount(async () => {
		try {
			const res = await fetch(`${API_BASE}/api/games/history?tma=${getTmaInitData()}`);
			history = await res.json();
		} catch (e) {
			console.error(e);
		}
	});
</script>

<div class="flex h-full flex-col justify-between p-5">
	<div class="space-y-6">
		<div class="space-y-3">
			<h1 class="text-4xl leading-none font-black tracking-tight">Sudoku Battle</h1>
		</div>

		<a
			href="/sudoku"
			class="block w-full card preset-filled-primary-500 p-5 no-underline transition-transform hover:scale-105"
		>
			<div class="flex items-center justify-between">
				<p class="text-2xl font-black">Новая игра</p>
				<PlayIcon />
			</div>
		</a>

		<a
			href="/sudoku?is_daily=true"
			class="block w-full card preset-filled-secondary-500 p-5 no-underline transition-transform hover:scale-105"
		>
			<div class="flex items-center justify-between">
				<p class="text-2xl font-black">Судоку дня</p>
				<PlayIcon />
			</div>
		</a>

		<div class="space-y-3">
			<h2 class="text-xl font-bold">История игр</h2>
			<div class="space-y-2">
				{#each history as game (game.game_id)}
					<a
						href="/sudoku?game_id={game.game_id}"
						class="flex items-center justify-between card p-3 hover:preset-filled-surface-100-900"
					>
						<span>Игра #{game.game_id}</span>
						<span class="text-xs opacity-60">{game.created_at.split('.')[0]}</span>
					</a>
				{/each}
			</div>
		</div>
		...

		<div class="grid grid-cols-2 gap-3">
			<a
				href="/leaderboard"
				class="block card preset-outlined-surface-200-800 p-4 no-underline transition-transform hover:scale-105"
			>
				<TrophyIcon class="mb-4 size-5" />
				<p class="text-lg font-bold">Лидерборд</p>
				<p class="mt-1 text-sm opacity-60">Таблица лучших игроков</p>
			</a>
			<a
				href="/profile"
				class="block card preset-outlined-surface-200-800 p-4 no-underline transition-transform hover:scale-105"
			>
				<UserRoundIcon class="mb-4 size-5" />
				<p class="text-lg font-bold">Профиль</p>
				<p class="mt-1 text-sm opacity-60">Статистика и прогресс</p>
			</a>
		</div>
	</div>
</div>
