import * as React from 'react';
import ListItem from '@mui/material/ListItem';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import ListSubheader from '@mui/material/ListSubheader';
import DashboardIcon from '@mui/icons-material/Dashboard';
import ShoppingCartIcon from '@mui/icons-material/ShoppingCart';
import PeopleIcon from '@mui/icons-material/People';
import BarChartIcon from '@mui/icons-material/BarChart';
import LayersIcon from '@mui/icons-material/Layers';
import AssignmentIcon from '@mui/icons-material/Assignment';
import { Link } from 'react-router-dom';
export const mainListItems = (

  <div>
    <ListItem button to="/" >
      <ListItemIcon>
        <DashboardIcon />
      </ListItemIcon>
      <Link button to="/" style={{ color: 'inherit', textDecoration: 'inherit' }}>
        <ListItemText primary="Dashboard" />
      </Link>
    </ListItem>

    {/* <ListItem button to="/sentiments">
      <ListItemIcon>
        <PeopleIcon />
      </ListItemIcon>
      <Link button to="/sentiments" style={{ color: 'inherit', textDecoration: 'inherit' }}>
        <ListItemText primary="Sentiments" />
      </Link>
    </ListItem> */}
    <ListItem button to="/sentiments">
      <ListItemIcon>
        <BarChartIcon />
      </ListItemIcon>
      <Link button to="/sentiments" style={{ color: 'inherit', textDecoration: 'inherit' }}>
        <ListItemText primary="Sentiment Analysis" />
      </Link>
    </ListItem>
  </div>

);

export const secondaryListItems = (
  <div>
    {/* <ListSubheader inset>Saved reports</ListSubheader>
    <ListItem button>
      <ListItemIcon>
        <AssignmentIcon />
      </ListItemIcon>
      <ListItemText primary="Current month" />
    </ListItem>
    <ListItem button>
      <ListItemIcon>
        <AssignmentIcon />
      </ListItemIcon>
      <ListItemText primary="Last quarter" />
    </ListItem>
    <ListItem button>
      <ListItemIcon>
        <AssignmentIcon />
      </ListItemIcon>
      <ListItemText primary="Year-end sale" />
    </ListItem> */}
  </div>
);
