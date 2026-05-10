<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	import { EraserIcon, PauseIcon, PlayIcon, Share2Icon } from '@lucide/svelte';
	import { getTmaInitData } from '$lib/tma';
	import { WS_BASE, BOT_USERNAME } from '$lib/config';
	import { goto } from '$app/navigation';

	const REG_SIZE = 3;
	const BOARD_SIZE = REG_SIZE * REG_SIZE;
	const numbers = Array.from({ length: BOARD_SIZE }, (_, index) => index + 1);

	let board = $state(Array.from({ length: BOARD_SIZE }, () => Array(BOARD_SIZE).fill(0)));
	let holes_mask = $state(Array.from({ length: BOARD_SIZE }, () => Array(BOARD_SIZE).fill(0)));
	let selectedCell = $state<{ row: number; col: number } | null>(null);
	let elapsedSeconds = $state(0);
	let isPaused = $state(false);
	let timerId: ReturnType<typeof setInterval> | null = null;
	let gameId = $state<number | null>(null);
	let socket: WebSocket | null = null;
	function connectWebSocket() {
		const params = new URLSearchParams(window.location.search);
		const id = params.get('game_id');
		if (id) gameId = parseInt(id);

		let url = `${WS_BASE}/ws/games/play?tma=${getTmaInitData()}`;
		if (gameId) url += `&game_id=${gameId}`;

		console.log('Connecting to:', url);
		socket = new WebSocket(url);

		socket.onopen = () => console.log('WebSocket Connected');

		socket.onmessage = (event) => {
			const data = JSON.parse(event.data);
			console.log('Received:', data);
			if (data.sudoku) {
				board = data.sudoku.table;
				holes_mask = data.sudoku.holes_mask;
				if (data.sudoku.holes_count == 0) {
					window.Telegram.WebApp.showPopup(
						{
							title: 'Игра окончена!',
							message: 'Вы успешно решили судоку! Начать новую игру?',
							buttons: [
								{ id: 'restart', type: 'default', text: 'Да, начать' },
								{ id: 'cancel', type: 'destructive', text: 'Выйти в главное меню' }
							]
						},
						(buttonId) => {
							if (buttonId === 'restart') {
								goto('/sudoku');
							} else {
								goto('/');
							}
						}
					);
				}
				if (!gameId) gameId = data.game_id;
				if (timerId === null) startTimer();
			} else if (data.penalty) {
				elapsedSeconds += data.penalty;
			}
		};
		socket.onerror = (err) => {
			window.Telegram.WebApp.showAlert('Ошибка подключения');
			console.error('WebSocket Error:', err);
		};
	}

	onMount(() => {
		connectWebSocket();
	});

	function makeMove(row: number, col: number, value: number): void {
		if (socket && socket.readyState === WebSocket.OPEN) {
			console.log('Sending move:', { row, col, value, time: elapsedSeconds });
			socket.send(JSON.stringify({ row, col, value, time: elapsedSeconds }));
		} else {
			console.error('Socket not open, state:', socket?.readyState);
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

		if (key >= '1' && key <= '9') {
			const num = parseInt(key);
			setNumber(num);
			event.preventDefault();
			return;
		}

		if (key === 'Backspace' || key === 'Delete') {
			clearCell();
			event.preventDefault();
			return;
		}

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

	function shareGame() {
		if (!gameId) return;
		const url = `https://t.me//${BOT_USERNAME}/sudoku?startapp=${gameId}`;
		window.Telegram.WebApp.openTelegramLink(
			`https://t.me/share/url?url=${encodeURIComponent(url)}&text=${encodeURIComponent('Давай разгадывать Судоку вместе!')}`
		);
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

	onDestroy(() => {
		stopTimer();
		if (socket) {
			socket.close();
		}
	});

	function classes(...values: Array<string | false | null | undefined>) {
		return values.filter(Boolean).join(' ');
	}
</script>

<svelte:window onkeydown={handleKeydown} />

<div class="flex h-full flex-col p-4 outline-hidden select-none">
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
							'flex aspect-square h-full w-full items-center justify-center text-2xl font-semibold',
							'border border-surface-400-600 hover:bg-surface-300-700 focus:z-10',

							(selectedCell?.row === rowIndex ||
								selectedCell?.col === colIndex ||
								(selectedCell &&
									Math.floor(selectedCell.row / REG_SIZE) === Math.floor(rowIndex / REG_SIZE) &&
									Math.floor(selectedCell.col / REG_SIZE) === Math.floor(colIndex / REG_SIZE))) &&
								'preset-filled-surface-200-800',
							selectedCell?.row === rowIndex &&
								selectedCell?.col === colIndex &&
								'preset-filled-surface-400-600',
							holes_mask[rowIndex][colIndex] && 'preset-filled-surface-100-900',
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
						class="btn h-10 w-10 preset-outlined-surface-200-800 p-0 btn-base text-2xl font-bold"
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
				<button type="button" class="btn-icon preset-filled-primary-500" onclick={shareGame}>
					<Share2Icon size={18} />
				</button>
			</div>
		</div>
	</div>
</div>
