import React, { useState, useEffect } from "react";
import axios from "axios";
import UnauthorizedPage from "../components/unauthorizedPage";
import ColumnGroupingTable from "../components/ColumnGroupingTable";
import TableCell from '@mui/material/TableCell';
import TableRow from '@mui/material/TableRow';
import LinePlot from "../components/linePlot"

import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';

function SimpleDashboard({ name, gender, birthday, diagnose, stage, dominantSide, lded, description, results, token }) {

  const [dataToPlot, setDataToPlot] = useState(null);
  const [selectedOption, setSelectedOption] = useState('stride length');

  const mapSelectedOption = {
    'stride length': 'stride length (cm)',
    'stride width': 'stride width (cm)',
    'stride time': 'stride time (s)',
    'velocity': 'velocity (m/s)',
    'cadence': 'cadence (1/min)',
    'turn time': 'turn time (s)',
  }

  const loadData = () => {
    let extractedDate = results.map(item => item['date']);
    let extractedValues = results.map(item => item[selectedOption]);
    let data = {
      'label': mapSelectedOption[selectedOption],
      'dates': extractedDate.reverse(),
      'values': extractedValues.reverse(),
    }
    setDataToPlot(data)
  }
  useEffect(() => {
    loadData();
  }, [results, selectedOption]);

  const handleOptionChange = (event) => {
    let newSelection = event.target.value
    setSelectedOption(newSelection);
  };

  const TopHeader = (
    <TableRow>
      <TableCell align="left" colSpan={1}>
        <b>Request information</b>
      </TableCell>
      <TableCell align="left" colSpan={6}>
        <b>Gait parameters</b>
      </TableCell>
    </TableRow>
  )

  const dashboard_columns = [
    // { 
    //   id: 'dateUpload',
    //   label: 'Upload Date',
    //   minWidth: 100, 
    //   color: '#131313',
    // },
    { 
      id: 'date',
      label: 'Experiment Date',
      minWidth: 100, 
      color: '#131313',
    },
    {
      id: 'stride length',
      label: 'Stride length (cm)',
      minWidth: 100,
      align: 'left',
      color: '#131313',
    },
    {
      id: 'stride width',
      label: 'Stride width (cm)',
      minWidth: 100,
      align: 'left',
      color: '#131313',
    },
    {
      id: 'stride time',
      label: 'Stride time (s)',
      minWidth: 100,
      align: 'left',
      color: '#131313',
    },
    {
      id: 'velocity',
      label: 'Velocity (m/s)',
      minWidth: 100,
      align: 'left',
      color: '#131313',
    },
    {
      id: 'cadence',
      label: 'Cadence (1/s)',
      minWidth: 100,
      align: 'left',
      color: '#131313',
    },
    {
      id: 'turn time',
      label: 'Turn time (s)',
      minWidth: 100,
      align: 'left',
      color: '#131313',
    },
  ];

  return (
    
        <div className="col-md-9">
          <div className="row">
            <div className="col-md-12">
              <div className="select-wrapper">
              <FormControl variant="standard" sx={{ m: 1, minWidth: 120 }}>
                <InputLabel id="demo-simple-select-standard-label">Gait parameters</InputLabel>
                <Select
                  labelId="demo-simple-select-standard-label"
                  id="demo-simple-select-standard"
                  value={selectedOption}
                  onChange={handleOptionChange}
                  label="Gait-parameter"
                >
                  <MenuItem value="">
                    <em>None</em>
                  </MenuItem>
                  <MenuItem value={'stride length'}>Stride Length</MenuItem>
                  <MenuItem value={'stride width'}>Stride Width</MenuItem>
                  <MenuItem value={'stride time'}>Stride Time</MenuItem>
                  <MenuItem value={'velocity'}>Velocity</MenuItem>
                  <MenuItem value={'cadence'}>Cadence</MenuItem>
                  <MenuItem value={'turn time'}>Turn time</MenuItem>
                </Select>
              </FormControl>
                
              </div>
              {dataToPlot === null ? <></> : <LinePlot dataToPlot={dataToPlot}/>}
              <ColumnGroupingTable columns={dashboard_columns} data={results} TopHeader={TopHeader} token={token}/>
            </div>
          </div>
        </div>

  )
}

export default SimpleDashboard