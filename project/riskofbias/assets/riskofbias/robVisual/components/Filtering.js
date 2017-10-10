import React from 'react';


class Filtering extends React.Component {

    render(){
        return (
            <div>
                <p>Filtering, please wait...&nbsp;
                    <span className='fa fa-spin fa-spinner'></span>
                </p>
            </div>
        );
    }
}

export default Filtering;
