<script>
	import { i18n } from '../i18n/i18n.js';
	import { socketState } from '../socket.svelte';
	import { user } from '../user.svelte';
	import Select from './Select.svelte';

	let username = $state("");
	let roomname = $state("");
	let tasktype = $state("");

	function handleSubmit(event) {
		event.preventDefault();
		socketState.joinRoom(username, roomname, tasktype);
	}

	function mapTaskOptions(tasks) {
		return tasks.map(task => {
			const obj = { value: task.name, title: i18n.t(task.label) }
			if (task.difficulty) {
				obj['subtitle'] = i18n.t(`difficulties.${task.difficulty}`)
			}
			return obj;
		});
	} 

	function getTaskOptions() {
		return fetch('/api/task-options')
			.then(resp => {
				if (!resp.ok) {
					throw new Error('Error loading data');
				}
				return resp.json();
			});
	}

	let tasksPromise = getTaskOptions();


</script>

<div style="margin: auto; width: 240px;">
	{#await tasksPromise}
		<p>{ i18n.t('task_load_info') }</p>
	{:then tasks}
		<p style="margin-bottom: 1.3rem;">{i18n.t('login_intro')}</p>
		<form
			onsubmit={handleSubmit}
		>
			<div class="form-control" style="margin-bottom: 0;">
				<label for="username" class="src-only">{i18n.t('username_field_label')}</label>
				<input id="username" bind:value={username} placeholder={i18n.t('username_field_label')} autocomplete="off" />
			</div>
			<div class="form-control" style="margin-bottom: 0;">
				<span class="src-only">Task</span>
				<Select options={mapTaskOptions(tasks)} bind:value={tasktype} placeholder={i18n.t('tasktype_select_label')} />
			</div>
			<div class="form-control">
				<label for="roomname" class="src-only">{i18n.t('roomname_field_label')}</label>
				<input id="roomname" bind:value={roomname} placeholder={i18n.t('roomname_field_label')} autocomplete="off" />
			</div>
			<div class="form-control">
				<button type="submit">{i18n.t('join_button_label')}</button>
			</div>
		</form>
	{:catch error}
		<p style="color: red;">{ i18n.t('task_load_error') } {error.message}</p>
	{/await}
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