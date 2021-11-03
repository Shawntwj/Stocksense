import { Switch, Route, Redirect, withRouter, BrowserRouter } from "react-router-dom";
import Dashboard from "./dashboard/Dashboard";
import Sentiments from "./sentiments/Sentiments";
const AppRoutes = () => {
  return (
    <Switch>
      <Route exact path="/" component={withRouter(Dashboard)} >
        {/* <Dashboard /> */}
      </Route>
      <Route exact path="/sentiments" component={withRouter(Sentiments)} >
        {/* <Sentiments /> */}
      </Route>
    </Switch>
  );
};

export default AppRoutes;
