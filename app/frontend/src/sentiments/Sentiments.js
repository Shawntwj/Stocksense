import * as React from 'react';
import { styled, createTheme, ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import MuiDrawer from '@mui/material/Drawer';
import Box from '@mui/material/Box';
import MuiAppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import List from '@mui/material/List';
import IconButton from '@mui/material/IconButton';
import Container from '@mui/material/Container';
import Grid from '@mui/material/Grid';
import Paper from '@mui/material/Paper';
import Link from '@mui/material/Link';
import MenuIcon from '@mui/icons-material/Menu';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import { mainListItems, secondaryListItems } from '../dashboard/listItems';
import { Typography, Divider, TextField } from '@mui/material';
import MenuItem from '@material-ui/core/MenuItem';
import GaugeChart from 'react-gauge-chart'
import ReactWordcloud from 'react-wordcloud';
import AdapterDateFns from '@mui/lab/AdapterDateFns';
import LocalizationProvider from '@mui/lab/LocalizationProvider';
import DatePicker from '@mui/lab/DatePicker';
import moment from 'moment';

import Chart from './Chart';
import Button from 'react-bootstrap/Button';

function Copyright(props) {
  return (
    <Typography variant="body2" color="text.secondary" align="center" {...props}>
      {'Copyright © '}
      <Link color="inherit">
        StockSense
      </Link>{' '}
      {new Date().getFullYear()}
      {'.'}
    </Typography>
  );
}

const drawerWidth = 240;

const AppBar = styled(MuiAppBar, {
  shouldForwardProp: (prop) => prop !== 'open',
})(({ theme, open }) => ({
  zIndex: theme.zIndex.drawer + 1,
  transition: theme.transitions.create(['width', 'margin'], {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  ...(open && {
    marginLeft: drawerWidth,
    width: `calc(100% - ${drawerWidth}px)`,
    transition: theme.transitions.create(['width', 'margin'], {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.enteringScreen,
    }),
  }),
}));

const Drawer = styled(MuiDrawer, { shouldForwardProp: (prop) => prop !== 'open' })(
  ({ theme, open }) => ({
    '& .MuiDrawer-paper': {
      position: 'relative',
      whiteSpace: 'nowrap',
      width: drawerWidth,
      transition: theme.transitions.create('width', {
        easing: theme.transitions.easing.sharp,
        duration: theme.transitions.duration.enteringScreen,
      }),
      boxSizing: 'border-box',
      ...(!open && {
        overflowX: 'hidden',
        transition: theme.transitions.create('width', {
          easing: theme.transitions.easing.sharp,
          duration: theme.transitions.duration.leavingScreen,
        }),
        width: theme.spacing(7),
        [theme.breakpoints.up('sm')]: {
          width: theme.spacing(9),
        },
      }),
    },
  }),
);

const mdTheme = createTheme();

const words = [
  {
    text: 'told',
    value: 64,
  },
  {
    text: 'moon',
    value: 50,
  },
  {
    text: 'hold',
    value: 100,
  },
  {
    text: 'bad',
    value: 30,
  },
]

function DashboardContent() {
  const [open, setOpen] = React.useState(true);
  const toggleDrawer = () => {
    setOpen(!open);
  };


  const [model, setModel] = React.useState('');
  const [stock, setStock] = React.useState('');
  const [data, setData] = React.useState('');
  const [ml, setMl] = React.useState('');
  const [value, setValue] = React.useState(new Date());
  const handleModelChange = (event) => {
    setModel(event.target.value);
  };

  const handleDataChange = (event) => {
    setData(event.target.value);
  };

  const handleMlChange = (event) => {
    setMl(event.target.value);
  };

  const handleStockChange = (event) => {
    setStock(event.target.value);
  };

  const handleClick = async () => {
    //console.log(stock, model, value, ml, data);
    let date = moment(value).format("YYYY-MM-DD");
    var url = `http://localhost:8000/api/${data}/${stock}/${date}`
    
    console.log(url)
    let response = await fetch(url)
    let res = await response.json()
    
    console.log(res)
    return res
  }
  return (
    <ThemeProvider theme={mdTheme}>
      <Box sx={{ display: 'flex' }}>
        <CssBaseline />
        <AppBar position="absolute" open={open}>
          <Toolbar
            sx={{
              pr: '24px', // keep right padding when drawer closed
            }}
          >
            <IconButton
              edge="start"
              color="inherit"
              aria-label="open drawer"
              onClick={toggleDrawer}
              sx={{
                marginRight: '36px',
                ...(open && { display: 'none' }),
              }}
            >
              <MenuIcon />
            </IconButton>
            <Typography
              component="h1"
              variant="h6"
              color="inherit"
              noWrap
              sx={{ flexGrow: 1 }}
            >
              StockSense
            </Typography>

          </Toolbar>
        </AppBar>
        <Drawer variant="permanent" open={open}>
          <Toolbar
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'flex-end',
              px: [1],
            }}
          >
            <IconButton onClick={toggleDrawer}>
              <ChevronLeftIcon />
            </IconButton>
          </Toolbar>
          <Divider />
          <List>{mainListItems}</List>
          <Divider />
          <List>{secondaryListItems}</List>
        </Drawer>
        <Box
          component="main"
          sx={{
            backgroundColor: (theme) =>
              theme.palette.mode === 'light'
                ? theme.palette.grey[100]
                : theme.palette.grey[900],
            flexGrow: 1,
            height: '100vh',
            overflow: 'auto',
          }}
        >
          <Toolbar />
          <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            <Grid container spacing={3}>
              {/* select options */}

              <Grid item xs={12}>
                <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
                  <div style={{ textAlign: "left", paddingLeft: 20, paddingBottom: 10 }}>
                    <Typography variant="h6">Analysis Parameters</Typography>
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'row' }}>
                    <Grid item xs={3} style={{ paddingLeft: 20 }}>
                      <TextField
                        value={data}
                        onChange={handleDataChange}
                        select // tell TextField to render select
                        label="Social Media"
                        style={{ minWidth: "100%" }}
                      >
                        <MenuItem key={"twitter"} value="twitter">
                          Twitter
                        </MenuItem>
                        <MenuItem key={"reddit"} value="reddit">
                          Reddit
                        </MenuItem>
                        <MenuItem
                          key={"stocktwits"} value="stocktwits">
                          Stocktwits
                        </MenuItem>
                        <MenuItem key={"news"} value="news">
                          News
                        </MenuItem>
                      </TextField>
                    </Grid>
                    <Grid item xs={3} style={{ paddingLeft: 20 }}>
                      <TextField
                        value={stock}
                        onChange={handleStockChange}
                        select // tell TextField to render select
                        label="Stock"
                        style={{ minWidth: "100%" }}
                      >
                        <MenuItem key={"AAPL"} value="aapl">
                          AAPL
                        </MenuItem>
                        <MenuItem key={"RUI"} value="rui">
                          RUI
                        </MenuItem>
                        <MenuItem key={"AMZN"} value="amzn">
                          AMZN
                        </MenuItem>
                        <MenuItem key={"ARKK"} value="arkk">
                          ARKK
                        </MenuItem>
                        <MenuItem key={"ATER"} value="ater">
                          ATER
                        </MenuItem>
                        <MenuItem key={"GOOGL"} value="googl">
                          GOOGL
                        </MenuItem>
                        <MenuItem key={"TSLA"} value="tsla">
                          TSLA
                        </MenuItem>
                        <MenuItem key={"VXRT"} value="vxrt">
                          VXRT
                        </MenuItem>
                      </TextField>
                    </Grid>
                    <Grid item xs={3} style={{ paddingLeft: 20 }}>
                      <TextField
                        value={model}
                        onChange={handleModelChange}
                        select // tell TextField to render select
                        label="Sentiment Model"
                        style={{ minWidth: "100%" }}
                      >
                        <MenuItem key={"vader"} value="vader">
                          Vader
                        </MenuItem>
                      </TextField>
                    </Grid>
                    <Grid item xs={3} style={{ paddingLeft: 20 }}>
                      <TextField
                        value={ml}
                        onChange={handleMlChange}
                        select // tell TextField to render select
                        label="ML Model"
                        style={{ minWidth: "100%" }}
                      >
                        <MenuItem key={"fbprophet"} value="fbprophet">
                          fbprophet
                        </MenuItem>

                      </TextField>
                    </Grid>
                  </div>
                  <div style={{ paddingTop: 10, flexDirection: 'row', display: "flex", alignSelf: "flex-start" }}>
                    <Grid item style={{ paddingLeft: 20, paddingTop: 10 }}>
                      <LocalizationProvider dateAdapter={AdapterDateFns}>
                        <DatePicker
                          label="Date"
                          value={value}
                          onChange={(newValue) => {
                            setValue(newValue);
                          }}
                          renderInput={(params) => <TextField {...params} />}
                        />
                      </LocalizationProvider>
                    </Grid>

                    <Grid item style={{ paddingLeft: 20, paddingTop: 12 }}>
                      {/* <Button variant="contained" size="large" style={{ width: "50%", minWidth: 100 }}>
                        Generate
                      </Button> */}
                      <Button onClick={handleClick}
                        style={{ backgroundColor: "#1976D2", padding: "16px 35px", color: "white", border: "none", borderRadius: 5, cursor: "pointer", fontSize: 16 }}
                      >
                        Generate
                      </Button>
                    </Grid>

                  </div>
                </Paper>
              </Grid>
              {/* model results/ correlation */}
              <Grid item xs={12} md={4} lg={5}>
                <Paper
                  sx={{
                    p: 2,
                    paddingLeft: 5,
                    display: 'flex',
                    flexDirection: 'column',
                    height: 240,
                    textAlign: "left"
                  }}
                >
                  <Grid item style={{ paddingBottom: 10 }}>
                    <Typography variant="h6" style={{ fontWeight: "bold" }}>Results</Typography>
                  </Grid>
                  <Grid item>
                    Correlation Score (price and sentiment): 0.803
                  </Grid>
                  <Grid item>
                    Correlation Score (volume and sentiment): 0.803
                  </Grid>
                  <Grid item>
                    <Typography style={{ fontWeight: "bold" }}>Decision: BUY</Typography>
                  </Grid>
                  <Grid item>
                    <Typography style={{ fontWeight: "bold" }}>Confidence Score: 80%</Typography>
                  </Grid>
                  {/* <Grid item>
                    <div style={{ height: 150 }}>
                      <ReactWordcloud words={words} />
                    </div>
                  </Grid> */}
                </Paper>
              </Grid>
              {/* Sentiment*/}
              <Grid item xs={12} md={4} lg={4} >
                <Paper
                  sx={{
                    p: 2,
                    display: 'flex',
                    flexDirection: 'column',
                    height: 240,
                    // background: "#1976D2"
                  }}
                >
                  <Typography variant="h6" style={{ fontWeight: "bold" }}>Word Cloud</Typography>

                  <div style={{ height: 150 }}>
                    <ReactWordcloud words={words} />
                  </div>
                </Paper>
              </Grid>

              {/* Sentiment*/}
              <Grid item xs={12} md={4} lg={3} >
                <Paper
                  sx={{
                    p: 2,
                    display: 'flex',
                    flexDirection: 'column',
                    height: 240,
                    background: "#1976D2"
                  }}
                >
                  <Typography style={{ fontWeight: "bold", color: "white", paddingBottom: 5 }}>Overall Sentiment</Typography>
                  <GaugeChart
                    hideText={true}
                    percent={0.78}
                    colors={['#EA4228', '#F5CD19', '#5BE12C']}
                  />
                  {/* <Typography variant="h5" style={{ color: "white" }}> 0.78 </Typography> */}
                  <Typography variant='h6' style={{ color: "white", fontWeight: "bold" }}> Positive </Typography>
                </Paper>
              </Grid>

              <Grid item xs={12}>
                <Paper
                  sx={{
                    p: 2,
                    display: 'flex',
                    flexDirection: 'column',
                    height: 240,
                  }}
                >
                  <Chart />
                </Paper>
              </Grid>
            </Grid>

            <Copyright sx={{ pt: 4 }} />
          </Container>
        </Box>
      </Box >
    </ThemeProvider >
  );
}

const Sentiments = () => {
  return <DashboardContent />;
}

export default Sentiments;