<script>
  import Router from "svelte-spa-router";
  import UserCreate from "./routes/UserCreate.svelte"

  const routes = {
    "/user-create": UserCreate,
  }

</script>

<Router {routes}/>