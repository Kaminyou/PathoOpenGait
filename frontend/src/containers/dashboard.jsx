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

function DashBoardPage({ token }) {

  const [name, setName] = useState('');
  const [gender, setGender] = useState('');
  const [birthday, setBirthday] = useState('');

  const [diagnose, setDiagnose] = useState('');
  const [stage, setStage] = useState('');
  const [dominantSide, setDominantSide] = useState('');
  const [lded, setLDED] = useState('');
  const [description, setDescription] = useState('');

  const [results, setResults] = useState([]);

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
    // let extractedDate = gaitData.map(item => item['date']);
    // let extractedValues = gaitData.map(item => item[newSelection]);
    // let data = {
    //   'label': newSelection,
    //   'dates': extractedDate,
    //   'values': extractedValues
    // }
    // setDataToPlot(data)
  };

  const fetchDefault = async () => {
    try {
      const response = await axios.get("/api/user/profile/personal", {
        headers: { Authorization: 'Bearer ' + token }
      });
      const { name, gender, birthday, diagnose, stage, dominantSide, lded, description } = response.data.profile;
      setName(name);
      setGender(gender);
      setBirthday(birthday);
      setDiagnose(diagnose);
      setStage(stage);
      setDominantSide(dominantSide);
      setLDED(lded);
      setDescription(description);
    } catch (error) {
      console.error(error);
    }
  };
  
  useEffect(() => {
    fetchDefault();
  }, []);

  const fetchResults = async () => {
    await axios.get("/api/user/request/results", {
      headers: {Authorization: 'Bearer ' + token}
    })
    .then((res) => {
      setResults(res.data.results)
    })
    .catch((error) => {
      console.error(error);
    });
  }

  useEffect(() => {
    fetchResults();
  }, [])

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

  if (!token) {
    // Render unauthorized page or redirect to unauthorized route
    return (
      <UnauthorizedPage/>
    )
  }

  return (
    <div className="padding-block">
    <div className="container">
      <div className="row">
        <div className="col-md-3">
          <h3>Patient Profile</h3>
          <div className="panel panel-default">
            <div className="panel-body">
              <h4>Basic information</h4>
              <p><strong>Name:</strong> {name}</p>
              <p><strong>Gender:</strong> {gender}</p>
              <p><strong>Birthday:</strong> {birthday}</p>
            </div>
          </div>
          <div className="panel panel-default">
            <div className="panel-body">
              <h4>Diagnosis</h4>
              <p><strong>Diagnose:</strong> {diagnose}</p>
              <p><strong>Stage:</strong> {stage}</p>
            </div>
          </div>
          <div className="panel panel-default">
            <div className="panel-body">
              <h4>Additional Information</h4>
              <p><strong>Dominant Side:</strong> {dominantSide}</p>
              <p><strong>LDED:</strong> {lded}</p>
              <p><strong>Description:</strong> {description}</p>
            </div>
          </div>
        </div>
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
      </div>
    </div>
  </div>
  )
}

export default DashBoardPage