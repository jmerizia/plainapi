import Tooltip from '@material-ui/core/Tooltip';
import { withStyles, Theme } from '@material-ui/core/styles';


const LightTooltip = withStyles((theme: Theme) => ({
    tooltip: {
      backgroundColor: 'lightgreen',
      color: 'rgba(0, 0, 0, 0.87)',
      boxShadow: 'none',
      fontSize: '17px',
    },
    arrow: {
        color: 'lightgreen',
    },
}))(Tooltip);

export default LightTooltip;