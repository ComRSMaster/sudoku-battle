<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	import { EraserIcon, PauseIcon, PlayIcon } from '@lucide/svelte';

	const REG_SIZE = 3;
	const BOARD_SIZE = REG_SIZE * REG_SIZE;
	const numbers = Array.from({ length: BOARD_SIZE }, (_, index) => index + 1);

	let board = $state(Array.from({ length: BOARD_SIZE }, () => Array(BOARD_SIZE).fill(0)));
	let selectedCell = $state<{ row: number; col: number } | null>(null);
	let elapsedSeconds = $state(0);
	let isPaused = $state(false);
	let timerId: ReturnType<typeof setInterval> | null = null;
	let gameId = $state<number | null>(null);
	let userId = 1;

	async function createGame(): Promise<void> {
		try {
			const response = await fetch('/api/games/', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ user_id: userId, holes_count: 5 })
			});
			const data = await response.json();
			gameId = data.game_id;
			board = data.sudoku.table;
		} catch (error) {
			console.error('Failed to create game:', error);
		}
	}

	async function loadGame(): Promise<void> {
		if (gameId === null) return;
		try {
			const response = await fetch(`/api/games/${gameId}?user_id=${userId}`);
			const data = await response.json();
			board = data.sudoku.table;
		} catch (error) {
			console.error('Failed to load game:', error);
		}
	}

	async function makeMove(row: number, col: number, value: number): Promise<void> {
		if (gameId === null) return;
		try {
			const response = await fetch(`/api/games/${gameId}/move`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ user_id: userId, row, col, value })
			});
			const data = await response.json();
			board = data.sudoku.table;
		} catch (error) {
			console.error('Failed to make move:', error);
		}
	}

	function selectCell(row: number, col: number) {
		if (isPaused) return;
		selectedCell = { row, col };
	}

	function setNumber(num: number) {
		if (isPaused || selectedCell === null) return;
		makeMove(selectedCell.row, selectedCell.col, num);
	}

	function clearCell() {
		if (isPaused || selectedCell === null) return;
		makeMove(selectedCell.row, selectedCell.col, 0);
	}

	function togglePause() {
		isPaused = !isPaused;
	}

	function handleKeydown(event: KeyboardEvent) {
		if (isPaused) return;

		const key = event.key;

		// Цифры 1-9
		if (key >= '1' && key <= '9') {
			const num = parseInt(key);
			setNumber(num);
			event.preventDefault();
			return;
		}

		// Backspace или Delete для очистки
		if (key === 'Backspace' || key === 'Delete') {
			clearCell();
			event.preventDefault();
			return;
		}

		// Стрелки для перемещения
		if (selectedCell !== null) {
			let newRow = selectedCell.row;
			let newCol = selectedCell.col;

			switch (key) {
				case 'ArrowUp':
					newRow = Math.max(0, selectedCell.row - 1);
					break;
				case 'ArrowDown':
					newRow = Math.min(BOARD_SIZE - 1, selectedCell.row + 1);
					break;
				case 'ArrowLeft':
					newCol = Math.max(0, selectedCell.col - 1);
					break;
				case 'ArrowRight':
					newCol = Math.min(BOARD_SIZE - 1, selectedCell.col + 1);
					break;
				case 'Escape':
					selectedCell = null;
					event.preventDefault();
					return;
				default:
					return;
			}

			selectCell(newRow, newCol);
			event.preventDefault();
		}
	}

	function startTimer() {
		if (timerId !== null) return;
		timerId = setInterval(() => {
			if (!isPaused) {
				elapsedSeconds += 1;
			}
		}, 1000);
	}

	function stopTimer() {
		if (timerId === null) return;
		clearInterval(timerId);
		timerId = null;
	}

	function formatTime(seconds: number) {
		const minutes = Math.floor(seconds / 60)
			.toString()
			.padStart(2, '0');
		const secs = (seconds % 60).toString().padStart(2, '0');
		return `${minutes}:${secs}`;
	}

	onMount(() => {
		startTimer();
		createGame();
	});

	onDestroy(() => {
		stopTimer();
	});

	function classes(...values: Array<string | false | null | undefined>) {
		return values.filter(Boolean).join(' ');
	}
</script>

<svelte:window onkeydown={handleKeydown} />

<div class="flex h-full flex-col p-4 focus:outline-none">
	<div class="flex flex-1 flex-col items-center justify-center gap-4 sm:flex-row">
		<div
			class="grid w-[min(calc(100vw-4rem),calc(100vh-22rem),36rem)] grid-cols-9 overflow-hidden card border-3 border-surface-700-300 shadow-xl"
		>
			{#each board as row, rowIndex (rowIndex)}
				{#each row as cell, colIndex (colIndex)}
					<button
						type="button"
						disabled={isPaused}
						onclick={() => selectCell(rowIndex, colIndex)}
						class={classes(
							'flex aspect-square h-full w-full items-center justify-center text-lg font-semibold',
							'border border-surface-400-600 hover:bg-surface-100-900 focus:z-10 focus:outline-hidden',
							(selectedCell?.row === rowIndex ||
								selectedCell?.col === colIndex ||
								(selectedCell &&
									Math.floor(selectedCell.row / REG_SIZE) == Math.floor(rowIndex / REG_SIZE) &&
									Math.floor(selectedCell.col / REG_SIZE) == Math.floor(colIndex / REG_SIZE))) &&
								'preset-filled-surface-100-900',
							selectedCell?.row === rowIndex &&
								selectedCell?.col === colIndex &&
								'preset-filled-surface-200-800 hover:bg-surface-200-800',
							rowIndex % REG_SIZE === REG_SIZE - 1 &&
								rowIndex !== BOARD_SIZE - 1 &&
								'border-b-3 border-b-surface-700-300',
							colIndex % REG_SIZE === REG_SIZE - 1 &&
								colIndex !== BOARD_SIZE - 1 &&
								'border-r-3 border-r-surface-700-300'
						)}
					>
						{cell !== 0 && !isPaused ? cell : ''}
					</button>
				{/each}
			{/each}
		</div>

		<div class="card preset-outlined-surface-200-800 p-3">
			<div class="text-surface-900-900 mb-2 flex items-center justify-between gap-3">
				<div>
					<div class="text-surface-700-900 text-xs tracking-[0.2em] uppercase">Время</div>
					<div class="font-mono text-2xl font-semibold">{formatTime(elapsedSeconds)}</div>
				</div>
				<button
					type="button"
					class={classes(
						'btn-icon',
						isPaused ? 'preset-filled-success-500' : 'preset-filled-warning-500'
					)}
					onclick={togglePause}
					aria-label={isPaused ? 'Возобновить' : 'Пауза'}
				>
					{#if isPaused}
						<PlayIcon size={18} />
					{:else}
						<PauseIcon size={18} />
					{/if}
				</button>
			</div>
			<div class="grid grid-cols-3 gap-2">
				{#each numbers as number (number)}
					<button
						type="button"
						class="btn h-10 w-10 preset-outlined-surface-200-800 p-0 btn-base font-bold"
						onclick={() => setNumber(number)}
						disabled={isPaused}
					>
						{number}
					</button>
				{/each}
			</div>
			<div class="mt-3 flex justify-center gap-2">
				<button
					type="button"
					class="btn-icon preset-filled-error-500"
					onclick={clearCell}
					disabled={isPaused}
				>
					<EraserIcon size={18} />
				</button>
			</div>
		</div>
	</div>
</div>
