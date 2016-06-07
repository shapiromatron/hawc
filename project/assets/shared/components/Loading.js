import React from 'react';


class Loading extends React.Component {

    render(){
        return (
            <div>
                <p>Loading, please wait...&nbsp;
                    <span className='fa fa-spin fa-spinner'></span>
                </p>
            </div>
        );
    }
}

export default Loading;
