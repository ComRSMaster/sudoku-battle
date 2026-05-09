<script lang="ts">
	import { PlayIcon, TrophyIcon, UserRoundIcon } from '@lucide/svelte';
</script>

<div class="flex h-full flex-col justify-between p-5">
	<div class="space-y-6">
		<div class="space-y-3">
			<h1 class="text-4xl font-black leading-none tracking-tight">
				Sudoku Battle
			</h1>
			<p class="max-w-[28ch] text-sm leading-6 opacity-70">
				Играй в судоку и соревнуйся с другими игроками.
			</p>
		</div>

		<a
			href="/sudoku"
			class="card preset-filled-primary-500 block w-full p-5 no-underline transition-transform hover:scale-105"
		>
			<div class="flex items-start justify-between gap-4">
				<div class="space-y-2">
					<p class="text-xs font-semibold uppercase tracking-[0.16em] opacity-70">
						Play
					</p>
					<p class="text-2xl font-black">Разгадывание судоку</p>
					<p class="max-w-[24ch] text-sm opacity-80">
						Открыть игровое поле.
					</p>
				</div>
				<div class="rounded-2xl bg-black/10 p-3">
					<PlayIcon class="size-6" />
				</div>
			</div>
		</a>

		<div class="grid grid-cols-2 gap-3">
			<a
				href="/leaderboard"
				class="card preset-outlined-surface-200-800 block p-4 no-underline transition-transform hover:scale-105"
			>
				<TrophyIcon class="mb-4 size-5" />
				<p class="text-lg font-bold">Лидерборд</p>
				<p class="mt-1 text-sm opacity-60">Таблица лучших игроков</p>
			</a>
			<a
				href="/profile"
				class="card preset-outlined-surface-200-800 block p-4 no-underline transition-transform hover:scale-105"
			>
				<UserRoundIcon class="mb-4 size-5" />
				<p class="text-lg font-bold">Профиль</p>
				<p class="mt-1 text-sm opacity-60">Статистика и прогресс</p>
			</a>
		</div>
	</div>
</div>
