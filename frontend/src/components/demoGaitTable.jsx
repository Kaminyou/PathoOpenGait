import React, { useState, useEffect } from "react";
import UploadButton from "../components/uploadButton"
import { Checkbox, FormGroup, FormControlLabel } from '@mui/material';

import LinePlot from "./linePlot"

function DemoGaitTable({ token, gaitUnit, gaitData, patientInfo }) {
  const [dataToPlot, setDataToPlot] = useState(null);
  const [selectedOption, setSelectedOption] = useState('stride_length');

  const loadData = () => {
    let extractedDate = gaitData.map(item => item['date']);
    let extractedValues = gaitData.map(item => item[selectedOption]);
    let data = {
      'label': selectedOption,
      'dates': extractedDate,
      'values': extractedValues
    }
    setDataToPlot(data)
  }
  useEffect(() => {
    loadData();
  }, []);

  const handleOptionChange = (event) => {
    let newSelection = event.target.value
    setSelectedOption(newSelection);
    let extractedDate = gaitData.map(item => item['date']);
    let extractedValues = gaitData.map(item => item[newSelection]);
    let data = {
      'label': newSelection,
      'dates': extractedDate,
      'values': extractedValues
    }
    setDataToPlot(data)
  };

  

  return (
    <>
      <h3>Personal information</h3>
      <table class="table">
        <tbody>
          {Object.entries(patientInfo).map(([key, value]) => (
            <tr key={key}>
              <td>{key}</td>
              <td>{value}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h3>Gait Trial Records</h3>
      <h4>Visualization</h4>
      <div>
        <label htmlFor="data-option"></label>
        <select id="data-option" value={selectedOption} onChange={handleOptionChange}>
          <option value="stride_length">Stride Length</option>
          <option value="stride_width">Stride Width</option>
          <option value="stride_time">Stride Time</option>
          <option value="velocity">Velocity</option>
        </select>
      </div>
      {dataToPlot === null ? <></> : <LinePlot dataToPlot={dataToPlot}/>}
      
      
      <h4>Records</h4>
      <table class="table">
        <thead>
        <tr>
            {Object.values(gaitUnit).map((columnName) => (
            <th scope="col" key={columnName}>{columnName}</th>
            ))}
        </tr>
        </thead>
        <tbody>
        {gaitData.map((rowData, index) => (
            <tr key={index}>
            {Object.keys(gaitUnit).map((key) => (
                <td key={key}>{rowData[key]}</td>
            ))}
            </tr>
        ))}
        </tbody>
    </table>
    </>
  )
}

export default DemoGaitTable