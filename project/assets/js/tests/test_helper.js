import { expect } from 'chai';
import sinon from 'sinon';
import chai from 'chai';
import chaiImmutable from 'chai-immutable';

global.expect = expect;
global.sinon = sinon;
chai.use(chaiImmutable);
