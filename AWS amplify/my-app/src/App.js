import './App.css';
import AWS from 'aws-sdk';
import React, { Component } from 'react';

AWS.config.update({
  accessKeyId: 'AKIAXKEHNJ4JK5DUERVW',
  secretAccessKey: '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',
  region: 'us-east-1'
});

const iotdata = new AWS.IotData({endpoint: 'https://a2lfjupb1otf51-ats.iot.us-east-1.amazonaws.com'});

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      bpmInput: '',
      timeSignatureInput: '',
      titleInput: ''
    };

    this.handleInputChange = this.handleInputChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleInputChange(event) {
    this.setState({
      [event.target.name]: event.target.value
    });
  }

  handleSubmit(event) {
    event.preventDefault();

    let message = {};
    if (this.state.titleInput) {
      message = {
        "metronomeID": '124', // replace with your metronome id
        "inputDATA": {
          "title": this.state.titleInput
        }
      };
    } else if (this.state.bpmInput && this.state.timeSignatureInput) {
      message = {
        "metronomeID": '124', // replace with your metronome id
        "inputDATA": {
          "bpm": this.state.bpmInput,
          "time_signature": this.state.timeSignatureInput
        }
      };
    } else {
      alert('Invalid input. Please fill in either the Title or both the BPM and Time Signature.');
      return;
    }

    const params = {
      topic: 'user/input',
      payload: JSON.stringify(message),
      qos: 0
    };

    iotdata.publish(params, (err, data) => {
      if (err) {
        console.log('Error', err);
      } else {
        console.log('Success', data);
      }
    });
  }

  render() {
    return (
      <div className="App">
        <h1>TENSONOME</h1>
        <form onSubmit={this.handleSubmit} className="form">
          <div className="grouped-inputs">
            <label>
              BPM:
              <input
                type="text"
                name="bpmInput"
                value={this.state.bpmInput}
                onChange={this.handleInputChange}
              />
            </label>
            <label>
              Time Signature:
              <input
                type="text"
                name="timeSignatureInput"
                value={this.state.timeSignatureInput}
                onChange={this.handleInputChange}
              />
            </label>
          </div>
          <hr />
          <label>
            Title:
            <input
              type="text"
              name="titleInput"
              value={this.state.titleInput}
              onChange={this.handleInputChange}
            />
          </label>
          <button type="submit">Submit</button>
        </form>
      </div>
    );
  }
}

export default App;
