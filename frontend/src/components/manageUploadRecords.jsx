import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import TableCell from '@mui/material/TableCell';
import TableRow from '@mui/material/TableRow';
import ColumnGroupingTable from '../components/ColumnGroupingTable'

function ManageUploadRecords({ token }) {
  const [records, setRecords] = useState([]);
  const MINUTE_MS = 2000; // 2 sec

  const fetchRecords = async () => {
    await axios.get("/api/manage/request/status", {
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

  useEffect(() => {
    const interval = setInterval(() => {
      fetchRecords();
      }, MINUTE_MS);
    return () => clearInterval(interval);
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

  const dashboard_columns = [
    { 
      id: 'dateUpload',
      label: 'Upload Date',
      minWidth: 100, 
      color: '#131313',
    },
    { 
      id: 'date',
      label: 'Trial Date',
      minWidth: 100, 
      color: '#131313',
    },
    { 
      id: 'trialID',
      label: 'Trial ID',
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

export default ManageUploadRecords;