import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import TableCell from '@mui/material/TableCell';
import TableRow from '@mui/material/TableRow';
import ColumnGroupingTable from '../components/ColumnGroupingTable'

function UploadRecords({ token }) {
  const [records, setRecords] = useState([]);

  const fetchRecords = async () => {
    await axios.get("/api/user/request/status", {
      headers: {Authorization: 'Bearer ' + token}
    })
    .then((res) => {
      setRecords(res.data.records)
    })
    .catch((error) => {
      console.error(error);
    });
  }

  useEffect(() => {
    fetchRecords();
  }, [])

  const TopHeader = (
    <TableRow>
      <TableCell align="left" colSpan={3}>
        <b>Request information</b>
      </TableCell>
      <TableCell align="left" colSpan={1}>
        <b>Results</b>
      </TableCell>
    </TableRow>
  )


  const uploadRecords = [
    { 
      uploadDate: '2023-06-01',
      experimentDate: 'Data 1',
      description: 'Description 1',
      computingStatus: 'Processing'
    },
    { 
      uploadDate: '2023-06-05',
      experimentDate: 'Data 2',
      description: 'Description 2',
      computingStatus: 'Completed'
    },
    { 
      uploadDate: '2023-06-10',
      experimentDate: 'Data 3',
      description: 'Description 3',
      computingStatus: 'Failed'
    }
    // Add more records as needed
  ];

  const dashboard_columns = [
    { 
      id: 'dateUpload',
      label: 'Upload Date',
      minWidth: 100, 
      color: '#131313',},
    { 
      id: 'date',
      label: 'Experiment Date',
      minWidth: 100, 
      color: '#131313',
    },
    {
      id: 'description',
      label: 'Description',
      minWidth: 100,
      align: 'left',
      color: '#131313',
    },
    {
      id: 'status',
      label: 'Status',
      minWidth: 100,
      align: 'left',
      format: (value) => value.toLocaleString('en-US'),
      color: '#131313',
    },
  ];
  
  return (
    <ColumnGroupingTable columns={dashboard_columns} data={records} TopHeader={TopHeader} token={token}/>
  );
}

export default UploadRecords;