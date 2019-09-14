﻿using System.Collections;
using System.Collections.Generic;
using UnityEngine;

[RequireComponent(typeof(FieldOfView))]
public class Cohesion : MonoBehaviour
{
    Rigidbody rigidbody;
    FieldOfView fieldOfView;

    // Start is called before the first frame update
    void Start()
    {
        rigidbody = GetComponent<Rigidbody>();
        fieldOfView = GetComponent<FieldOfView>();
    }

    Vector3 CalcForce()
    {
        List<GameObject> boidObjs = fieldOfView.GetVisibleBoids();
        Vector3 resultant = new Vector3();
        foreach (GameObject boid in boidObjs)
        {
            resultant += boid.transform.position;
        }
        return (resultant /= boidObjs.Count()) - transform.position;
    }

    // Update is called once per frame
    void FixedUpdate()
    {
        rb.AddForce(CalcForce());
    }
}
