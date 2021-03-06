import * as React from 'react';
import { useTheme } from '@mui/material/styles';
import {
    ComposedChart,
    Line,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    Scatter
} from 'recharts';
import moment from 'moment';
// import Grid from '@mui/material/Grid';
// import DateRangePicker from '@wojtekmaj/react-daterange-picker';
// import { Typography } from '@mui/material';

// const data = [
//     {
//         date: "20/10/2021",
//         negative: 590,
//         positive: 800,
//         volume: 1400,
//         cnt: 490,
//     },
//     {
//         date: '21/10/2021',
//         negative: 868,
//         positive: 967,
//         volume: 1506,
//         cnt: 590,
//     },
//     {
//         date: '22/10/2021',
//         negative: 1397,
//         positive: 1098,
//         volume: 989,
//         cnt: 350,
//     },
//     {
//         date: '23/10/2021',
//         negative: 1480,
//         positive: 1200,
//         volume: 1228,
//         cnt: 480,
//     },
//     {
//         date: '24/10/2021',
//         negative: 1520,
//         positive: 1108,
//         volume: 1100,
//         cnt: 460,
//     },
//     {
//         date: '25/10/2021',
//         negative: 1400,
//         positive: 680,
//         volume: 1700,
//         cnt: 380,
//     },
// ];

export default function Chart({ data, type }) {
    const theme = useTheme();
    const [value, onChange] = React.useState([new Date(), new Date()]);

    return (
        <React.Fragment>

            {/* <Grid container spacing={3}>
                <Grid item>
                    <Typography variant="body1" style={{ paddingLeft: 10 }}> Price and C:</Typography>
                </Grid>
            </Grid> */}
            <ResponsiveContainer width="100%" height="100%">
                {type == "price" ?
                    <ComposedChart
                        width={500}
                        height={100}
                        data={data}
                        margin={{
                            top: 20,
                            right: 20,
                            bottom: 20,
                            left: 20,
                        }}
                    >
                        <CartesianGrid stroke="#f5f5f5" />
                        {/* <XAxis dataKey="date" scale="band" /> */}

                        <YAxis />
                        <Tooltip />
                        <Legend />
                        {/* <Area type="monotone" dataKey="amt" fill="#8884d8" stroke="#8884d8" /> */}
                        <Bar dataKey="negative" barSize={20} fill="#EA4228" />
                        <Bar dataKey="positive" barSize={20} fill="#209c05" />

                        <XAxis textAnchor="end"
                            tick={{ angle: -45 }} minTickGap={-200} dataKey="date" tickFormatter={timeStr => moment(timeStr).format("Do MMM, hA")} interval={0} allowDataOverflow={true} height={100} />
                        {/* <Line type="monotone" dataKey="price" stroke="#ff7300" /> */}
                        {/* <Scatter dataKey="cnt" fill="red" /> */}
                    </ComposedChart> : <ComposedChart
                        width={500}
                        height={400}
                        data={data}
                        margin={{
                            top: 20,
                            right: 20,
                            bottom: 20,
                            left: 20,
                        }}
                    >
                        <CartesianGrid stroke="#f5f5f5" />
                        <XAxis textAnchor="end"
                            tick={{ angle: -45 }} minTickGap={-200} dataKey="date" tickFormatter={timeStr => moment(timeStr).format("Do MMM, hA")} interval={100} allowDataOverflow={true} height={100} />
                        <YAxis domain={['auto', 'auto']} />
                        <Tooltip />
                        <Legend />
                        {/* <Area type="monotone" dataKey="amt" fill="#8884d8" stroke="#8884d8" /> */}
                        {/* <Bar dataKey="negative" stackId="a" barSize={20} fill="#EA4228" />
                        <Bar dataKey="positive" stackId="a" barSize={20} fill="#209c05" />*/}
                        <Line type="monotone" dataKey="predicted" stroke="red" />
                        <Line type="monotone" dataKey="test" stroke="green" />
                        <Line type="monotone" dataKey="train" stroke="blue" strokeDasharray="5 5" />

                    </ComposedChart>}
            </ResponsiveContainer>
        </React.Fragment>
    );
}
