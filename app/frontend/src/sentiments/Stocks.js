import * as React from 'react';
import Link from '@mui/material/Link';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
// import Title from './Title';

// Generate Stocks Data
function createData(id, date, source, comments, score) {
  return { id, date, source, comments, score };
}

const rows = [
  createData(
    0,
    '16 Mar, 2019',
    'News',
    'I am going to hold',
    0.9,
  ),
  createData(
    1,
    '16 Mar, 2019',
    'Twitter',
    'Do not sell, hold!',
    0.8,

  ),
  createData(
    2,
    '16 Mar, 2019',
    'Twitter',
    'Buying tomorrow',
    0.4,
  ),
  createData(
    3,
    '15 Mar, 2019',
    'StockTwits',
    'sell',
    -0.3,
  ),
];

function preventDefault(event) {
  event.preventDefault();
}

export default function Stocks({ data }) {
  return (
    <React.Fragment>
      {/* <Title>Recent Stock Prices</Title> */}
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>Timestamp</TableCell>
            <TableCell>Comments</TableCell>
            <TableCell>Sentiment Score</TableCell>
            <TableCell align="right">Sentiment Result</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {data?.length > 0 && data.map((row) => (
            <TableRow key={row.id}>
              <TableCell>{row.datetime}</TableCell>
              <TableCell>{row.content}</TableCell>
              <TableCell>{row.score}</TableCell>
              <TableCell align="right">{row.sentiment}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      {/* <Link color="primary" href="#" onClick={preventDefault} sx={{ mt: 3 }}>
        See more Stocks
      </Link> */}
    </React.Fragment>
  );
}
