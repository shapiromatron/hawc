// https://observablehq.com/@munnsmunns/epicyclic-gearing@503
export default function define(runtime, observer) {
  const main = runtime.module();
  main.variable(observer("graphic")).define("graphic", ["d3", "gears", "gear"], function (d3, gears, gear) {
    const svg = d3.create("svg")
      .attr("viewBox", [-0.53, -0.53, 1.06, 1.06])
      .attr("stroke", "#2b353a")
      .attr("stroke-width", 3 / 640)
      .style("max-width", "320px")
      .style("display", "block")
      .style("margin", "auto")
      .style("background", "default");

    const frame = svg.append("g");

    const path = frame.selectAll("path")
      .data(gears)
      .join("path")
      .attr("fill", d => d.fill)
      .attr("d", gear);

    return Object.assign(svg.node(), {
      update(angle, frameAngle) {
        path.attr("transform", d => `translate(${d.origin}) rotate(${(angle / d.radius) % 360})`);
        frame.attr("transform", `rotate(${frameAngle % 360})`);
      }
    });
  }
  );
  main.define("initial angle", function () {
    return (
      0
    )
  });
  main.variable(observer("mutable angle")).define("mutable angle", ["Mutable", "initial angle"], (M, _) => new M(_));
  main.variable(observer("angle")).define("angle", ["mutable angle"], _ => _.generator);
  main.define("initial frameAngle", function () {
    return (
      0
    )
  });
  main.variable(observer("mutable frameAngle")).define("mutable frameAngle", ["Mutable", "initial frameAngle"], (M, _) => new M(_));
  main.variable(observer("frameAngle")).define("frameAngle", ["mutable frameAngle"], _ => _.generator);
  main.variable(observer("update")).define("update", ["graphic", "mutable angle", "speed", "mutable frameAngle"], function* (graphic, $0, speed, $1) {
    while (true) {
      for (let index = 0; index < 230; ++index) {
        yield graphic.update(
          $0.value += speed * (Math.sin(index * 0.02) + 0.8),
          $1.value += (speed * (Math.sin(index * 0.02) + 0.8)) / 0.5
        );
      }
      for (let index = 0; index < 50; ++index) {
        yield graphic.update($0.value, $1.value)
      }
    }
  }
  );
  main.variable(observer("gears")).define("gears", ["x", "y"], function (x, y) {
    return (
      [
        { fill: "#2b353a", teeth: 80, radius: -0.5, origin: [0, 0], annulus: true },
        { fill: "#2b353a", teeth: 16, radius: +0.1, origin: [0, 0] },
        { fill: "#003d7b", teeth: 32, radius: -0.2, origin: [0, -0.3] },
        { fill: "#67bf53", teeth: 32, radius: -0.2, origin: [-0.3 * x, -0.3 * y] },
        { fill: "#ed792c", teeth: 32, radius: -0.2, origin: [0.3 * x, -0.3 * y] }
      ]
    )
  });
  main.variable(observer("x")).define("x", function () {
    return (
      Math.sin(2 * Math.PI / 3)
    )
  });
  main.variable(observer("y")).define("y", function () {
    return (
      Math.cos(2 * Math.PI / 3)
    )
  });
  main.variable(observer("toothRadius")).define("toothRadius", function () {
    return (
      0.008
    )
  });
  main.variable(observer("holeRadius")).define("holeRadius", function () {
    return (
      0.02
    )
  });
  main.variable(observer("speed")).define("speed", function () {
    return (
      0.2
    )
  });
  main.variable(observer("gear")).define("gear", ["toothRadius", "holeRadius"], function (toothRadius, holeRadius) {
    return (
      function gear({ teeth, radius, annulus }) {
        const n = teeth;
        let r2 = Math.abs(radius);
        let r0 = r2 - toothRadius;
        let r1 = r2 + toothRadius;
        let r3 = holeRadius;
        if (annulus) r3 = r0, r0 = r1, r1 = r3, r3 = r2 + toothRadius * 3;
        const da = Math.PI / n;
        let a0 = -Math.PI / 2 + (annulus ? Math.PI / n : 0);
        const path = ["M", r0 * Math.cos(a0), ",", r0 * Math.sin(a0)];
        let i = -1;
        while (++i < n) {
          path.push(
            "A", r0, ",", r0, " 0 0,1 ", r0 * Math.cos(a0 += da), ",", r0 * Math.sin(a0),
            "L", r2 * Math.cos(a0), ",", r2 * Math.sin(a0),
            "L", r1 * Math.cos(a0 += da / 3), ",", r1 * Math.sin(a0),
            "A", r1, ",", r1, " 0 0,1 ", r1 * Math.cos(a0 += da / 3), ",", r1 * Math.sin(a0),
            "L", r2 * Math.cos(a0 += da / 3), ",", r2 * Math.sin(a0),
            "L", r0 * Math.cos(a0), ",", r0 * Math.sin(a0)
          );
        }
        path.push("M0,", -r3, "A", r3, ",", r3, " 0 0,0 0,", r3, "A", r3, ",", r3, " 0 0,0 0,", -r3, "Z");
        return path.join("");
      }
    )
  });
  main.variable(observer("d3")).define("d3", function () {
    return (
      d3
    )
  });
  return main;
}
