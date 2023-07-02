import React, { useState } from "react";
import axios from "axios";

import DemoSubmit from "../components/demoSubmit"
import DemoGaitTable from "../components/demoGaitTable"

function DemoPage({ token }) {
  const [checked, setChecked] = useState(false);
  const [gaitData, setGaitData] = useState(null);
  const [gaitUnit, setGaitUnit] = useState(null);
  const [patientInfo, setPatientInfo] = useState(null);

  const handleChange = () => {
    setChecked(!checked)
  }

  const onSubmit = async (e) => {
    e.preventDefault();
    await axios.get("/api/demo/patient/gait/data", {
      headers: {Authorization: 'Bearer ' + 'ddd'}
    })
    .then((res) => {
      setGaitData(res.data.data);
    })
    .catch((error) => {
      console.error(error);
    });

    await axios.get("/api/demo/patient/gait/unit", {
      headers: {Authorization: 'Bearer ' + 'ddd'}
    })
    .then((res) => {
      setGaitUnit(res.data.data);
    })
    .catch((error) => {
      console.error(error);
    });

    await axios.get("/api/demo/patient/info", {
      headers: {Authorization: 'Bearer ' + 'ddd'}
    })
    .then((res) => {
      setPatientInfo(res.data.data);
    })
    .catch((error) => {
      console.error(error);
    });
  }

  return (
    <div className='padding-block'>
      <div className="container">
        <div className="row">
          <div className="col-xs-12 col-md-10">
            <div className="about-text">
              <h2>Demo</h2>
              {(gaitData === null || gaitUnit === null || patientInfo === null) ? <>
                <DemoSubmit token={token} checked={checked} handleChange={handleChange} onSubmit={onSubmit}/>
              </>:<>
                <DemoGaitTable token={token} gaitData={gaitData} gaitUnit={gaitUnit} patientInfo={patientInfo}/>
              </>}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DemoPage