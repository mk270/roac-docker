import React, { Component } from 'react';
import { BrowserRouter as Router, Route, Link } from "react-router-dom";

import './App.css';

import ApolloClient from "apollo-boost";
import { ApolloProvider, Query } from "react-apollo";
import gql from "graphql-tag";

import { base_url } from "./endpoint"; // for base_url

const client = new ApolloClient({
  uri: base_url
});

function nodelist_to_object(nl) {
    function remap(prev, curr) {
        prev[curr.node.detailId] = curr.node.detailValue;
        return prev;
    }
    return nl.reduce(remap, {});
}

class Book extends React.Component {
  render() {
      var details = nodelist_to_object(this.props.details);
      var bookLink = "/book/" + this.props.bookUuid;
      return (
              <section class="spotlight" key={this.props.bookUuid}>
						<div><a href={details.overview_url}><img src={details.cover_url} alt="{this.props.title}" height="241" width="160" /></a></div>
						<div class="content">
							<h3>{this.props.title}</h3>
							<p>DOI: {details.doi}</p>
                            <br/>
                            <br/>
						</div>
					</section>

      )
  }
}

const Books = () => (
  <Query query={gql`
      {
        allBooks {
          nodes {
            title
            pageCount
            bookUuid
            bookDetailsByBookUuid {
              edges {
                node {
                 detailId
                 detailValue
                }
              }
            }
          }
        }
      }
   `}
  >
    {({ loading, error, data }) => {
      if (loading) return <p>Loading ...</p>;
      if (error) return <p>Error :(</p>;

      return data.allBooks.nodes.map((
          { title, pageCount, bookUuid, bookDetailsByBookUuid }) => (
              <Book bookUuid={bookUuid} pageCount={pageCount}
                    title={title} details={bookDetailsByBookUuid.edges} />
          ));
   }}
  </Query>
);

class BookDetailCard extends React.Component {
  render() {
      var details = nodelist_to_object(this.props.details);
      var bookLink = "/book/" + this.props.bookUuid;
      return (
        <div key={this.props.bookUuid}>
          <p>{`${this.props.title}: ${this.props.pageCount}`}</p>
          <p><a href={details.overview_url}>buy</a></p>
          <a href={details.overview_url}>
            <img src={details.cover_url} alt="{title}" height="241" width="160" />
          </a>
        </div>
      )
  }
}


const BookPage = ({match}) => (
  <ApolloProvider client={client}>
  <Query query={gql`
      {
        allBooks(condition: {
          bookUuid: "${match.params.bookUuid}"
        }) {
          nodes {
            title
            pageCount
            bookUuid
            bookDetailsByBookUuid {
              edges {
                node {
                 detailId
                 detailValue
                }
              }
            }
          }
        }
      }
   `}
  >
    {({ loading, error, data }) => {
      if (loading) return <p>Loading ...</p>;
      if (error) return <p>Error :(</p>;

      return data.allBooks.nodes.map((
          { title, pageCount, bookUuid, bookDetailsByBookUuid }) => (
              <BookDetailCard bookUuid={bookUuid} pageCount={pageCount}
                    title={title} details={bookDetailsByBookUuid.edges} />
          ));
   }}
  </Query>
  </ApolloProvider>
);

const AllBooks = () => (
     <div>
        <h2>All Books</h2>
        <ApolloProvider client={client}>
           <Books />
        </ApolloProvider>
     </div>
);

class App extends Component {
  render() {
      return (
          <div><AllBooks /></div>
      );
  }
}

export default App;
