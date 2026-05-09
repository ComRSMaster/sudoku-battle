<script lang="ts">
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';
	import { page } from '$app/state';
	import { TrophyIcon, BookIcon, HouseIcon, UserIcon } from '@lucide/svelte';
	import { Navigation } from '@skeletonlabs/skeleton-svelte';

	interface NavLink {
		label: string;
		href: string;
		icon: any;
	}

	const links: NavLink[] = [
		{ label: 'Главная', href: '/', icon: HouseIcon },
		{ label: 'Sudoku', href: '/sudoku', icon: BookIcon },
		{ label: 'Рейтинг', href: '/leaderboard', icon: TrophyIcon },
		{ label: 'Профиль', href: '/profile', icon: UserIcon }
	];

	function isActive(href: string): boolean {
		return page.url.pathname === href;
	}

	function classes(...values: Array<string | false | null | undefined>) {
		return values.filter(Boolean).join(' ');
	}

	let { children } = $props();
</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>

<div class="flex h-screen w-screen flex-col bg-surface-50-950">
	<div class="flex-1 overflow-auto">
		{@render children()}
	</div>

	<Navigation layout="bar" class="border-t border-surface-200-800">
		<Navigation.Menu class="grid grid-cols-4 gap-2 p-2">
			{#each links as link (link.label)}
				{@const Icon = link.icon}
				<a
					href={link.href}
					class={classes(
						'flex min-h-16 flex-col items-center justify-center rounded-xl px-2 py-2 text-center no-underline transition-colors',
						isActive(link.href) ? 'preset-filled-primary-500' : 'preset-outlined-surface-200-800'
					)}
				>
					<Icon class="size-5" />
					<span class="text-xs font-semibold">{link.label}</span>
				</a>
			{/each}
		</Navigation.Menu>
	</Navigation>
</div>
