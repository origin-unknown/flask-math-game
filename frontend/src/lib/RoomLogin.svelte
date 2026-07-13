<script>
  import { socketState } from '../socket.svelte';
  import { user } from '../user.svelte';

  let username = $state("");
  let roomname = $state("");

  function handleSubmit(event) {
  	event.preventDefault();
  	socketState.joinRoom(username, roomname);
  }
</script>

<div style="margin: auto; width: 240px;">
    <p style="margin-bottom: 1.3rem;">Please enter a username and, optionally, a room name to join.</p>
    <form
        onsubmit={handleSubmit}
    >
        <div class="form-control" style="margin-bottom: 0;">
            <label for="username" class="src-only">Username</label>
            <input id="username" bind:value={username} placeholder="Username" />
        </div>
        <div class="form-control">
            <label for="roomname" class="src-only">Roomname</label>
            <input id="roomname" bind:value={roomname} placeholder="Roomname" />
        </div>
        <div class="form-control">
            <button type="submit">Join</button>
        </div>
    </form>
</div>

<style>

.src-only {
    display: none;
}

.form-control {
    margin-bottom: .6em;
}

label, input, button {
    box-sizing:border-box;
    width: 100%;
    padding: 1em;
    margin: 0;
}

input {
    border: 1px solid #505054; 
    border-radius: 6px; 
}

input#username {
    border-bottom-right-radius: 0;
    border-bottom-left-radius: 0;
}

input#roomname {
    border-top-right-radius: 0;
    border-top-left-radius: 0;
}

</style>