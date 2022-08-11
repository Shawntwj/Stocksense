import * as React from 'react';
import Link from '@mui/material/Link';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Title from './Title';

// Generate Stocks Data
function createData(id, date, name, volume, score, amount, correlation) {
  return { id, date, name, volume, score, amount, correlation };
}

const rows = [
  createData(
    0,
    '16 Mar, 2019',
    'AMZN',
    '10,000',
    'placeholder',
    312.44,
    0.9
  ),
  createData(
    1,
    '16 Mar, 2019',
    'GOOGL',
    '10,000',
    'placeholder',
    866.99,
    0.5
  ),
  createData(2, '16 Mar, 2019', 'ARKK', '10,000', 'placeholder', 100.81, -0.9),
  createData(
    3,
    '16 Mar, 2019',
    'AAPL',
    '10,000',
    'placeholder',
    654.39,
    0.3
  ),
  createData(
    4,
    '15 Mar, 2019',
    'RUI',
    '10,000',
    'placeholder',
    212.79,
    -0.3
  ),
];

function preventDefault(event) {
  event.preventDefault();
}

export default function Stocks() {
  return (
    <React.Fragment>
      <Title>Recent Stock Prices</Title>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>Date</TableCell>
            <TableCell>Stocks</TableCell>
            <TableCell>Volume</TableCell>
            <TableCell>Sentiment Score</TableCell>
            <TableCell>Price</TableCell>
            <TableCell align="right">Correlation</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {rows.map((row) => (
            <TableRow key={row.id}>
              <TableCell>{row.date}</TableCell>
              <TableCell>{row.name}</TableCell>
              <TableCell>{row.volume}</TableCell>
              <TableCell>{row.score}</TableCell>
              <TableCell>{`$${row.amount}`}</TableCell>
              <TableCell align="right">{row.correlation}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      <Link color="primary" href="#" onClick={preventDefault} sx={{ mt: 3 }}>
        See more Stocks
      </Link>
    </React.Fragment>
  );
}
