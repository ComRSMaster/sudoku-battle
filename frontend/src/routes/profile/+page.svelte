<script lang="ts">
	import { onMount } from 'svelte';
	import { API_BASE } from '$lib/config';
	import { getTmaInitData } from '$lib/tma';

	interface UserInfo {
		user_id: number;
		username: string | null;
		name: string;
		photo_url: string;
		solved_count: number;
		achievements: {
			sprinter: boolean;
			advanced_player: boolean;
		};
	}

	let userInfo = $state<UserInfo | null>(null);
	let loading = $state(true);

	async function loadUserPosition() {
		try {
			loading = true;
			const response = await fetch(`${API_BASE}/api/users/?tma=${getTmaInitData()}`);
			const data = await response.json();
			userInfo = data;
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
		<p class="text-sm font-semibold tracking-[0.16em] uppercase opacity-60">Профиль</p>
	</div>

	{#if loading}
		<div class="flex items-center justify-center">
			<p class="text-sm opacity-60">Загрузка профиля...</p>
		</div>
	{:else if userInfo}
		<div class="card preset-filled-primary-500 p-5">
			<p class="text-sm tracking-[0.16em] uppercase opacity-70">Ваш профиль</p>
			<h2 class="mt-2 text-3xl font-black">{userInfo.name}</h2>
			{#if userInfo.username}
				<p class="mt-1 text-sm opacity-80">@{userInfo.username}</p>
			{/if}
		</div>

		<div class="mt-5 grid grid-cols-2 gap-3">
			<div class="card preset-outlined-surface-200-800 p-4">
				<p class="text-xs tracking-[0.16em] uppercase opacity-50">Разгадано</p>
				<p class="mt-2 text-3xl font-black">{userInfo.solved_count}</p>
			</div>
			<div class="col-span-2 card preset-outlined-surface-200-800 p-4">
				<p class="mb-2 text-xs tracking-[0.16em] uppercase opacity-50">Достижения</p>
				<div class="flex gap-2">
					<span
						class="rounded px-2 py-1 text-xs font-bold uppercase {userInfo.achievements.sprinter
							? 'bg-green-500/20 text-green-400'
							: 'bg-surface-700 opacity-50'}">Спринтер</span
					>
					<span
						class="rounded px-2 py-1 text-xs font-bold uppercase {userInfo.achievements
							.advanced_player
							? 'bg-green-500/20 text-green-400'
							: 'bg-surface-700 opacity-50'}">Продвинутый игрок</span
					>
				</div>
			</div>
		</div>
	{/if}
</div>
