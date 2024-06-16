<script>
	// get today, 2 days back and 2 days forward
	let days = [];
	const before_today = 2;
	const after_today = 5;
	for (let i = -before_today; i <= after_today; i++) {
		const date = new Date();
		date.setDate(date.getDate() + i);
		days.push(date.toISOString().split('T')[0].split('-').splice(1, 2).reverse().join('/'));
	}
	// get today in MO TU WD
	const today = new Date().getDay().toString().replace('0', 'SU').replace('1', 'MO').replace('2', 'TU').replace('3', 'WD').replace('4', 'TH').replace('5', 'FR').replace('6', 'SA');
	const daynames = ['SU', 'MO', 'TU', 'WD', 'TH', 'FR', 'SA'];
	console.log(days)

	const tennis_men_games = fetch_games('data/tennis_men.json')
	const tennis_women_games = fetch_games('data/tennis_women.json')
	// read data/velo.json
	const velo_games = fetch_games('data/velo.json');

	const euros_games = fetch_games('data/football_euros.json');
	console.log(euros_games);

	function fetch_games(filepath) {
		return fetch(filepath)
		.then(response => response.json())
		.then(data => {
			data.forEach(game => {
				console.log(game);
				// get array of all days of the game
				const game_startday = game[1]
				const game_endday = game[2]
				const game_days = [];
				// dates are DD/MM, so we can compare them as strings
				for (let i = parseInt(game_startday.split('/')[0]); i <= parseInt(game_endday.split('/')[0]); i++) {
					game_days.push(i.toString() + '/' + game_startday.split('/')[1]);
				}
				let grid_start = null;
				let grid_end = null;
				days.forEach(day => {
					if (game_days.includes(day)) {
						if (grid_start === null) {
							grid_start = days.indexOf(day) + 1;
						}
						grid_end = days.indexOf(day) + 2;
					}
				});
				game[3] = grid_start;
				game[4] = grid_end;
				console.log(game);
			});
			return data;
		})
		.catch(error => {
			console.error('Error:', error);
		});
	}

</script>

<main>
	{#await euros_games then games}
	{#each games as game}
	{#if game[4] != null}
<div class='football game pad-h-m pad-v-m green border space-h-m space-v-m pop-m' style="grid-column: {game[3]} / {game[4]};">
  <h3 class='title'>{game[0]}</h3>
  <span class='game-right'>
    <i class='subtitle'>
      {#if game[5]}
        {game[6]} - {game[7]}
      {:else}
        {game[6]}
      {/if}
    </i>
    <i class='game-info subtitle'>euros</i>
  </span>
</div>
		{/if}
	{/each}
	{:catch error}
	{/await}
	{#each days as day}
	<div class='day sidebar pad-h-l pad-v-l' class:today={days.indexOf(day) - before_today == 0} style={'grid-column:' + (days.indexOf(day) + 1)}><span>{daynames[ (daynames.indexOf(today) + days.indexOf(day) + 5) % 7 ]} {day}</span></div>
	{/each}
	{#await tennis_men_games then games}
	{#each games as game}
	{#if game[4] != null}
	<div class='tennis tennis-men game pad-h-m pad-v-m green border space-h-m space-v-m pop-m' style={'grid-column:' + ' ' + game[3] + ' / '+  game[4] }><h3 class='title'>{game[0]}</h3><span class='game-right'><i class='subtitle '>{game[1]} - {game[2]}</i><i class='game-info subtitle'>men's tennis</i></span></div>
	{/if}
	{/each}
	{:catch error}
	{/await}
	{#await tennis_women_games then games}
	{#each games as game}
	{#if game[4] != null}
	<div class='tennis tennis-women game pad-h-m pad-v-m green border space-h-m space-v-m pop-m' style={'grid-column:' + ' ' + game[3] + ' / '+  game[4] }><h3 class='title'>{game[0]}</h3><span class='game-right'><i class='subtitle '>{game[1]} - {game[2]}</i><i class='game-info subtitle'>women's tennis</i></span></div>
	{/if}
	{/each}
	{:catch error}
	{/await}
	{#await velo_games then games}
	{#each games as game}
	{#if game[4] != null}
	<div class='velo game pad-h-m pad-v-m green border space-h-m space-v-m pop-m' style={'grid-column:' + ' ' + game[3] + ' / '+  game[4] }><h3 class='title'>{game[0]}</h3><span class='game-right'><i class='subtitle '>{game[1]} - {game[2]}</i><i class='game-info subtitle'>cycling</i></span></div>
	{/if}
	{/each}
	{:catch error}
	{/await}
</main>
