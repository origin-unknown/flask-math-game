<script>
  let { members = [] } = $props();
</script>

<ul id="roster">
{#each members.toSorted((a, b) => b.points - a.points) as member}
  <li id={member.sid} style=""><span>{member.username}</span> <span>{member.points}</span></li>
{/each}
</ul>

<style>
  #roster {
  	padding: 1rem;
  }
  #roster li {
  	display: flex;
  	width: 100%; 
  }

  #roster li span {
  	flex-grow: 1;
  }

  #roster li span:last-of-type {
  	flex-grow: 0;
  }
</style>