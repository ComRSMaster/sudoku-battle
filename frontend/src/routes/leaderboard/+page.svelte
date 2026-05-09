<script lang="ts">
	const leaderboard = [
		{ place: 1, name: 'Mila', score: 1280, streak: 12 },
		{ place: 2, name: 'Artem', score: 1215, streak: 9 },
		{ place: 3, name: 'Nika', score: 1180, streak: 8 },
		{ place: 4, name: 'Vlad', score: 1095, streak: 6 }
	];
</script>

<div class="flex h-full flex-col p-5">
	<div class="mb-5">
		<p class="text-sm font-semibold uppercase tracking-[0.16em] opacity-60">Leaderboard</p>
	</div>

	<div class="space-y-3">
		<h2 class="text-3xl font-black">Лучшие сегодня</h2>
		<p class="text-sm opacity-65">Таблица лучших игроков.</p>
	</div>

	<div class="mt-6 space-y-3">
		{#each leaderboard as player (player.place)}
			<div class="card preset-outlined-surface-200-800 flex items-center justify-between p-4">
				<div class="flex items-center gap-4">
					<div class="preset-filled-primary-500 flex h-10 w-10 items-center justify-center rounded-xl font-black">
						{player.place}
					</div>
					<div>
						<p class="font-bold">{player.name}</p>
						<p class="text-sm opacity-60">Streak: {player.streak} days</p>
					</div>
				</div>
				<div class="text-right">
					<p class="text-lg font-black">{player.score}</p>
					<p class="text-xs uppercase tracking-[0.14em] opacity-50">points</p>
				</div>
			</div>
		{/each}
	</div>
</div>