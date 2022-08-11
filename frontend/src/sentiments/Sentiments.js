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
import CheckIcon from '@mui/icons-material/Check';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import { mainListItems, secondaryListItems } from '../dashboard/listItems';
import { Typography, Divider, TextField } from '@mui/material';
import MenuItem from '@material-ui/core/MenuItem';
import GaugeChart from 'react-gauge-chart'
import ReactWordcloud from 'react-wordcloud';
// import AdapterDateFns from '@mui/lab/AdapterDateFns';
// import LocalizationProvider from '@mui/lab/LocalizationProvider';
// import DatePicker from '@mui/lab/DatePicker';
import moment from 'moment';
import ClearIcon from '@mui/icons-material/Clear';

import Chart from './Chart';
import Button from 'react-bootstrap/Button';
import Stocks from './Stocks';
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



function DashboardContent() {
  const [open, setOpen] = React.useState(true);
  const toggleDrawer = () => {
    setOpen(!open);
  };


  const [model, setModel] = React.useState('flair');
  const [stock, setStock] = React.useState('aapl');
  const [data, setData] = React.useState('twitter');
  const [ml, setMl] = React.useState('autoarima');
  const [value, setValue] = React.useState(new Date());

  const [corr, setCorr] = React.useState("");
  const [ystdPrice, setYstdPrice] = React.useState("");
  const [todayPrice, setTodayPrice] = React.useState("");
  const [decision, setDecision] = React.useState("");
  const [sentimentScore, setSentimentScore] = React.useState(0);
  const [error, setError] = React.useState("");
  const [words, setWords] = React.useState([])
  const [sentimentGraph, setSentimentGraph] = React.useState([])
  console.log(sentimentGraph)
  console.log("test")
  const [table, setTable] = React.useState([])
  const [graphData, setGraphData] = React.useState([])
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
    var url = `http://localhost:8000/api/${data}/${stock}/${model}/${ml}`
    console.log(url)
    let response = await fetch(url)
    let res = await response.json()

    let sentiment = res
    if (sentiment) {
      setCorr(sentiment.corr)
      setDecision(sentiment.decision)
      setError(sentiment.error)
      setSentimentScore(sentiment.score)
      setYstdPrice(sentiment.ytdClose)
      setTodayPrice(sentiment.todayPredict)
      setWords(sentiment.words)
      setSentimentGraph(sentiment.data)
      setTable(sentiment.top10)
      setGraphData(sentiment.graphData)
    }
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
                        <MenuItem key={"reddit:comment"} value="reddit:comment">
                          Reddit Comment
                        </MenuItem>
                        <MenuItem key={"reddit:post"} value="reddit:post">
                          Reddit Post
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
                        <MenuItem key={"flair"} value="flair">
                          Flair
                        </MenuItem>
                        <MenuItem key={"finbert"} value="finbert">
                          Finbert
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
                        <MenuItem key={"autoarima"} value="autoarima">
                          Autoarima
                        </MenuItem>
                        <MenuItem key={"arima"} value="arima">
                          Arima
                        </MenuItem>
                        <MenuItem key={"prophet"} value="prophet">
                          fbprophet
                        </MenuItem>
                        <MenuItem key={"LSTM"} value="LSTM">
                          LSTM
                        </MenuItem>
                        <MenuItem key={"lr"} value="lr">
                          Linear Regression
                        </MenuItem>
                      </TextField>
                    </Grid>
                  </div>
                  <div style={{ paddingTop: 10, flexDirection: 'row', display: "flex", alignSelf: "flex-end" }}>
                    <Grid item style={{ paddingLeft: 20, paddingTop: 10 }}>
                      {/* <LocalizationProvider dateAdapter={AdapterDateFns}>
                        <DatePicker
                          label="Date"
                          value={value}
                          onChange={(newValue) => {
                            setValue(newValue);
                          }}
                          renderInput={(params) => <TextField {...params} />}
                        />
                      </LocalizationProvider> */}
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
                    Correlation Score (price and sentiment):  {Math.round(corr * 100) / 100}
                  </Grid>
                  <Grid item container style={{ direction: "column" }}>
                    <Grid item>
                      Yesterday Price: ${Math.round(ystdPrice * 100) / 100}
                    </Grid>
                    <Grid item style={{ paddingLeft: 5 }}>
                      |
                    </Grid>
                    <Grid item style={{ paddingLeft: 5 }}>
                      Predicted Price: ${Math.round(todayPrice * 100) / 100}
                    </Grid>
                  </Grid>

                  <Grid item container style={{ direction: "column" }}>
                    {ystdPrice < todayPrice ?
                      <> <CheckIcon style={{ color: "green" }} /><Typography style={{ fontWeight: "bold", color: "green", paddingLeft: 5 }}>Predicted price {">"} yesterday price</Typography> </> :
                      todayPrice == ystdPrice ?
                        <> <CheckIcon style={{ color: "#ffa733" }} /><Typography style={{ fontWeight: "bold", color: "#ffa733", paddingLeft: 5 }}>Predicted price {"="} yesterday price</Typography></> :
                        <> <ClearIcon style={{ color: "red" }} /><Typography style={{ fontWeight: "bold", color: "red", paddingLeft: 5 }}>Predicted price {"<"} yesterday price</Typography></>
                    }
                  </Grid>
                  <Grid item container style={{ direction: "column" }}>
                    {corr > 0.2 || corr < -0.2 ?
                      <><CheckIcon style={{ color: "green" }} /><Typography style={{ fontWeight: "bold", color: "green", paddingLeft: 5 }}>High correlation score</Typography></> :
                      <><ClearIcon style={{ color: "red" }} /><Typography style={{ fontWeight: "bold", color: "red", paddingLeft: 5 }}>Low correlation score</Typography></>}
                  </Grid>
                  {/* <Grid item container style={{ direction: "column" }}>
                    <CheckIcon style={{ color: "green" }} /><Typography style={{ fontWeight: "bold", color: "green", paddingLeft: 5 }}>Sentiment score follows price trend</Typography>
                  </Grid> */}
                  <Grid item>
                    <Typography style={{ fontWeight: "bold" }}>RMSE Score: {Math.round(error * 100) / 100}</Typography>
                  </Grid>
                  <Grid item>
                    <Typography style={{ fontWeight: "bold", color: decision.toLowerCase() == "buy" ? "green" : decision.toLowerCase() == "sell" ? "red" : decision.toLowerCase() == "hold" ? "#ffa733" : "black" }}>Overall Decision: {decision}</Typography>
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

                  <div style={{ height: 200, width: "100%" }}>
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
                    percent={sentimentScore < 0 ? -sentimentScore / 2 : sentimentScore}
                    colors={['#EA4228', '#ffa733', '#5BE12C']}
                  />
                  {/* <Typography variant="h5" style={{ color: "white" }}> 0.78 </Typography> */}
                  <Typography variant='h6' style={{ color: "white", fontWeight: "bold" }}> {sentimentScore > 0 ? "Positive" : sentimentScore < 0 ? "Negative" : "Neutral"} </Typography>
                  <Typography variant='h6' style={{ color: "white" }}> {Math.round(sentimentScore * 100) / 100} </Typography>
                </Paper>
              </Grid>

              <Grid item xs={12}>
                <Paper
                  sx={{
                    p: 2,
                    display: 'flex',
                    flexDirection: 'column',
                    height: 400,
                  }}
                >
                  <Typography style={{ fontWeight: "bold" }}>Overall Sentiment for Today </Typography>
                  <Chart data={sentimentGraph} type={"price"} />
                </Paper>
              </Grid>

              <Grid item xs={12}>
                <Paper
                  sx={{
                    p: 2,
                    display: 'flex',
                    flexDirection: 'column',
                    height: 400,
                  }}
                >
                  <Typography style={{ fontWeight: "bold" }}>Train, Test and Predicted Price</Typography>
                  <Chart data={graphData} />
                </Paper>
              </Grid>


              <Grid item xs={12}>
                <Paper
                  sx={{
                    p: 2,
                    display: 'flex',
                    flexDirection: 'column',
                    height: "100%",
                  }}
                >
                  <Typography style={{ fontWeight: "bold" }}>Top 10 Posts/Comments with Highest Sentiment Score</Typography>
                  <Stocks data={table} />
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