function ProfilePanel({ name, gender, birthday, diagnose, stage, dominantSide, lded, description }) {

  return (
    <>
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
					<p><strong>LEDD:</strong> {lded}</p>
					<p><strong>Description:</strong> {description}</p>
				</div>
			</div>
		</>
  )
}

export default ProfilePanel